# THIS FILE HOUSES THE DETECTION ENGINE  (BLE drop-score / unstable-ratio / jamming)


# ETC IMPORTS
import requests, subprocess, threading, time, wave, os, tempfile, random
from pathlib import Path
from piper.voice import PiperVoice


# NSM IMPORTS
from nsm_vars import Variables


# CONSTANTS
console  = Variables.console
TTS_WAV  = os.path.join(tempfile.gettempdir(), f"tts_{os.getpid()}.wav")
MODEL    = str(Path(__file__).parent.parent / "database" / "en_US-lessac-medium.onnx")



def _dur(seconds):
    """This will say seconds under a minute, else minutes"""

    s = int(seconds)
    if s < 60: return f"{s} second{'' if s == 1 else 's'}"
    m = s // 60
    return f"{m} minute{'' if m == 1 else 's'}"



class Detector():
    """Measures detections — houses BLE + WiFi anomaly scoring and the ESP LED output."""



    class BLE():
        """BLE detection — aggregate drop-score + unstable-ratio scoring and alerting."""


        alpha             = 0.05
        avg               = None
        last_count        = 0
        prev_drop_pct     = 0
        prev_unstable_pct = 0
        unstable_devices  = set()
        started           = None
        floor             = 5
        jam_start         = 0
        thaw_after        = 60 * 20
        thaw_alpha        = 0.005
        jam_hits          = 0


        @classmethod
        def _average_ratio(cls, current_count):
            """This will track average device count over time, frozen while jammed"""


            if cls.avg is None: cls.avg = float(current_count); return 0.0

            if not Variables.jammed:
                alpha   = 0.01 if current_count < cls.avg else cls.alpha
                cls.avg = (cls.avg * (1 - alpha)) + (current_count * alpha)

            elif time.time() - cls.jam_start > cls.thaw_after:
                cls.avg = (cls.avg * (1 - cls.thaw_alpha)) + (current_count * cls.thaw_alpha)

            if cls.avg == 0: return 0.0
            score = (current_count - cls.avg) / cls.avg

            return round(score, 3)


        @classmethod
        def _score(cls, total, unstables, count):
            """One score vs the trigger (Variables.pct_set_drop) — over it = jam on, under = off"""


            unstable_pct = round((unstables / total) * 100, 2)
            drop_pct     = round((((cls.avg or 1) - count) / (cls.avg or 1)) * 100, 2)

            score = max(drop_pct, unstable_pct)
            over  = score > Variables.pct_set_drop and cls.avg >= cls.floor

            cls.jam_hits = cls.jam_hits + 1 if over else 0
            jam          = cls.jam_hits >= Variables.jam_consistent


            if jam != Variables.jammed:

                Variables.jammed = jam
                Variables.time_without_incidents = time.time()

                if jam:
                    cls.jam_start = time.time()
                    Notifications.drop_pct(drop_pct=score, title="BLE Jamming detected", cause=f"Score {score}% over {Variables.pct_set_drop}%  (drop {drop_pct} / unstable {unstable_pct})")

                console.print(f"[bold {'red' if jam else 'green'}][{'!] JAM' if jam else '+] clear'}:[/] {score}%  (drop {drop_pct} / unstable {unstable_pct})")


            cls.prev_drop_pct     = drop_pct
            cls.prev_unstable_pct = unstable_pct


        @classmethod
        def evaluate(cls, live_map, count):
            """Per-cycle BLE detection: classify each device, prune stale, then score the aggregate. Returns total tracked."""


            now = time.time()
            if cls.started is None: cls.started = now


            for mac, dev in list(live_map.items()):

                use          = f"[dim][>] {mac} ->"
                weight       = 0
                rssi_list    = dev["rssi_list"]
                time_missing = now - dev["last_seen"]


                # // C++ IS SUPERIOR
                if len(rssi_list) >= 3 and max(rssi_list) - min(rssi_list) > 30:
                    weight += 1
                    data = (f"{use}[yellow] rssi spike")

                    console.print(data)

                if (time_missing > 5):
                    weight += 1
                    #console.print(f"{use}[yellow] short time gap")

                if (time_missing > 10):
                    weight += 2
                    data = (f"{use}[yellow] long time gap")

                    console.print(data)


                if (weight >= 2): dev["unstable_hits"] += 1
                else:
                    if dev["unstable_hits"] > 0:
                        dev["unstable_hits"] -= 1


                if (dev["unstable_hits"] >= 2):
                    if dev["status"] != "unstable":
                        console.print(f"[bold red][!] Unstable Device:[yellow] {mac}")
                        cls.unstable_devices.add(mac)
                        dev["status"] = "unstable"
                        dev["stable_count"] = 0

                        vendor = dev["data"].get("vendor") or "Unknown"
                        Variables.push_event(f"Alert. Unstable BLE device detected. {vendor}")

                else:
                    if (dev["status"] == "unstable"):
                        dev["stable_count"] += 1

                        if (dev["stable_count"] >= 2):
                            dev["status"] = "stable"
                            dev["stable_count"] = 0
                            cls.unstable_devices.discard(mac)
                            data = (f"[bold green][+] Device now stable:[yellow] {mac}")
                            console.print(data)


                """
                Proverbs 27:17 As iron sharpens iron, so a friend sharpens another.
                """


                if time_missing > 30 and not Variables.jammed:
                    data = (f"[bold yellow][-] Removing stale device:[/bold yellow] {mac}")
                    console.print(data)
                    cls.unstable_devices.discard(mac)
                    del live_map[mac]



            total     = len(live_map) or 1
            unstables = len({mac for mac in cls.unstable_devices if mac in live_map})

            average = cls._average_ratio(current_count=count)
            Detector.LED.push_color(average_ratio=average)
            cls._score(total=total, unstables=unstables, count=count)

            cls.last_count        = count
            Variables.ble_current = total


            # NEW MAX / MIN DEVICE COUNT
            if total > Variables.ble_max:
                Variables.ble_max = total
                data = (f"[bold green][!] New BLE max:[/bold green] {total} devices")
                console.print(data)
                Variables.push_event(f"New maximum. {total} Bluetooth devices detected")

            if total < Variables.ble_min:
                Variables.ble_min = total
                data = (f"[bold red][!] New BLE min:[/bold red] {total} devices")
                console.print(data)
                Variables.push_event(f"Alert. Device count dropped to {total} Bluetooth devices")



    class WiFi():
        """WiFi detection — consumes normalized frame events. Deauth today; AP-drop / deauth-flood next."""


        last_deauth     = 0
        deauth_cooldown = 30
        alpha           = 0.05
        hourly          = {}
        pct_set         = 25
        good_ap         = True
        good_cl         = True
        interval        = 60


        @classmethod
        def consume(cls, ev):
            """Entry point — take one normalized WiFi frame event and run detection on it.

            ev = {"sub": <subtype>, "src": <ta>, "dst": <ra>, "ssid": <str|None>, "rssi": <int>, "channel": <str>}
            The same shape a tshark line OR the rust engine produces, so detection never cares who parsed it.
            """


            # DEAUTH  (management subtype 0x0c)
            if ev["sub"] == 0x0c: cls._deauth(ev)


        @classmethod
        def _deauth(cls, ev):
            """Deauth frame detected -> alert. Cooldown-gated so a flood doesn't spam the phone."""


            src     = ev["src"]
            dst     = ev["dst"]
            channel = ev["channel"]

            console.print(f"[bold red][DEAUTH][/bold red]  [red]{src}[/red]  [dim]->[/dim]  [red]{dst}[/red]  [dim]ch:[/dim][bold cyan]{channel}[/bold cyan]")

            if time.time() - cls.last_deauth <= cls.deauth_cooldown: return


            # who got hit? look the src/dst up against the AP presence map the monitor keeps
            aps     = Variables.live_map_wifi
            ap_ssid = aps[src]["ssid"] if src in aps else (aps[dst]["ssid"] if dst in aps else None)

            target  = None
            for ap in aps.values():
                if dst in ap.get("clients", {}):
                    target = dst
                    break

            Variables.push_event(f"Deauth frame detected on channel {channel}")
            Notifications.deauth(src=src, dst=dst, channel=channel, ap_ssid=ap_ssid, target=target)
            TTS.speak(kind="deauth", channel=channel, ap_ssid=ap_ssid)

            cls.last_deauth = time.time()


        @classmethod
        def _average(cls, hour, key, current):
            """This will track the average per hour for aps and clients over time, frozen while jammed"""


            slot = cls.hourly.setdefault(hour, {})

            if key not in slot: slot[key] = float(current); return 0.0

            if not Variables.jammed:
                alpha     = 0.01 if current < slot[key] else cls.alpha
                slot[key] = (slot[key] * (1 - alpha)) + (current * alpha)

            if slot[key] == 0: return 0.0

            return round((current - slot[key]) / slot[key], 3)


        @classmethod
        def _score(cls, aps, clients):
            """This will check ap/client counts against the hourly baseline and alert on deviations"""


            hour = time.localtime().tm_hour

            ap_ratio = cls._average(hour, "ap", aps)
            cl_ratio = cls._average(hour, "cl", clients)

            ap_pct = round(abs(ap_ratio) * 100, 2)
            cl_pct = round(abs(cl_ratio) * 100, 2)


            # AP
            if ap_pct > cls.pct_set and cls.good_ap:

                word = "spiked" if ap_ratio > 0 else "dropped"
                console.print(f"[bold red][!] AP count {word}:[/bold red] {aps} aps   {ap_pct}% off baseline")

                Variables.push_event(f"Alert. WiFi AP count {word} to {aps}")
                Notifications.device_count(device_count=aps, title=f"WiFi APs {word}")
                TTS.speak(kind="ap_count", word=word)

                cls.good_ap = False

            elif ap_pct < cls.pct_set / 2 and not cls.good_ap:

                console.print(f"[bold green][+] AP count back to baseline:[/bold green] {aps} aps")
                Notifications.device_count(device_count=aps, title="WiFi APs back to baseline", priority="default")

                cls.good_ap = True


            # CLIENT
            if cl_pct > cls.pct_set and cls.good_cl:

                word = "spiked" if cl_ratio > 0 else "dropped"
                console.print(f"[bold red][!] Client count {word}:[/bold red] {clients} clients   {cl_pct}% off baseline")

                Variables.push_event(f"Alert. WiFi client count {word} to {clients}")
                Notifications.device_count(device_count=clients, title=f"WiFi Clients {word}")

                cls.good_cl = False

            elif cl_pct < cls.pct_set / 2 and not cls.good_cl:

                console.print(f"[bold green][+] Client count back to baseline:[/bold green] {clients} clients")
                Notifications.device_count(device_count=clients, title="WiFi Clients back to baseline", priority="default")

                cls.good_cl = True


        @classmethod
        def watch(cls):
            """This will sample the area every interval and score it against the baseline"""


            def worker():

                while True:

                    time.sleep(cls.interval)

                    aps     = sum(1 for ap in list(Variables.live_map_wifi.values()) if time.time() - ap.get("last_seen", 0) <= Variables.wifi_ap_stale)
                    clients = sum(1 for ap in list(Variables.live_map_wifi.values()) for c in list(ap.get("clients", {}).values()) if c.get("status") in ("online", "idle"))

                    cls._score(aps=aps, clients=clients)


            threading.Thread(target=worker, args=(), daemon=True).start()
            console.print(f"[bold green][+] Successfully started WiFi baseline watcher!")



    class LED():
        """Parked ESP32 LED output — dormant unless Variables.esp_ip is set."""


        @classmethod
        def push_color(cls, average_ratio, timeout=3):
            """ratio -> color -> POST to an ESP32 LED server.  Only fires when Variables.esp_ip is configured."""


            # Green=Safe  Yellow=Caution  Orange=Warning  Red=Danger  Purple=Abnormal/Emergency
            if   average_ratio <= 0.0:  color = "green"
            elif average_ratio <= 0.25: color = "yellow"
            elif average_ratio <= 0.6:  color = "orange"
            elif average_ratio <= 1.0:  color = "red"
            else:                       color = "purple"


            if not Variables.esp_ip: return color   # parked until an ESP is wired in

            try:

                url      = f"http://{Variables.esp_ip}/?color={color}"
                response = requests.post(url=url, timeout=timeout)

                if response.status_code in [200, 204]: console.print(f"[bold green][+] LED pushed:[/bold green] {color} --> {Variables.esp_ip}")
                else:                                   console.print(f"[bold red][-] Failed to push to LED Server:[bold yellow] Status code: {response.status_code}")

            except Exception as e: console.print(f"[bold red]LED Exception Error:[bold yellow] {e}")

            return color





class Notifications():
    """This will be used to notify user of events happening"""


    # =======
    #  WiFi
    # =======
    @classmethod
    def deauth(cls, src:str, dst:str, channel, ap_ssid:str=None, target:str=None, priority="max"):
        """This will cls.push_ntfy <-- deauth frame detected"""

        headers = {
            "Title": "Deauth Frame Detected",
            "Priority": priority,
        }

        target_str = "broadcast (all clients)" if dst == "ff:ff:ff:ff:ff:ff" else (target or dst)
        ap_str     = f"  |  AP: {ap_ssid}" if ap_ssid else ""
        data       = f"Src: {src}  ->  {target_str}\nCh: {channel}{ap_str}"

        cls._push_ntfy(headers=headers, data=data, type="wifi")


    @classmethod
    def client_left(cls, ssid:str, client_mac:str, vendor_client:str, duration:str, priority="max"):
        """This will cls.push_ntfy <-- client_left"""

        headers = {
            "Title": f"Client left {ssid}",
            "Priority": priority,
        }
        data = f"Client: {client_mac}  Vendor: {vendor_client}  -->  {ssid}  Duration: {duration}"

        cls._push_ntfy(headers=headers, data=data, type="wifi")


    @classmethod
    def client_returned(cls, ssid:str, client_mac:str, vendor_client:str, duration:str, priority="default"):
        """This will cls.push_ntfy <-- client_returned"""

        headers = {
            "Title": f"Client returned to {ssid}",
            "Priority": priority,
        }
        data = f"Client: {client_mac}  Vendor: {vendor_client}  -->  {ssid}  Away for: {duration}"

        cls._push_ntfy(headers=headers, data=data, type="wifi")


    # ======
    #  BLE
    # =====
    @classmethod
    def device_count(cls, device_count:int, title:str, priority="max"):
        """This will be used to update user on max/min device count"""


        headers = {
            "Title": f"{title}",
            "Priority": priority,
        }
        data = f"{device_count} devices"

        cls._push_ntfy(headers=headers, data=data, type="ble")


    @classmethod
    def push_ble_device(cls, mac:str, vendor:str, name:str=None, priority="low"):
        """This will cls.push_ntfy <-- new BLE device"""

        headers = {
            "Title": "New BLE Device",
            "Priority": priority,
        }
        data = f"Name: {name or 'Unknown'}  MAC: {mac}  Vendor: {vendor or 'Unknown'}"


        cls._push_ntfy(headers=headers, data=data, type="ble")


    @classmethod
    def unstable_devices_pct(cls,  unstable_pct:float, title:str="BLE Instability Alert", cause="Possible BLE/Bluetooth Jamming", priority="max"):
        """This will cls.push_ntfy <-- unstable_devices"""

        headers = {
            "Title": title,
            "Priority": priority,
        }
        data = f"Unstable Percentage: {unstable_pct}%\n{cause}"


        cls._push_ntfy(headers=headers, data=data, type="ble")

    
    @classmethod
    def drop_pct(cls, drop_pct:float, title:str = "BLE Device Drop Alert", cause="A large spike of BLE/Bluetooth devices have dropped in a short timeframe!", priority="max"):
        """This will cls.push_ntfy <-- drop_score"""

        headers = {
            "Title": title,
            "Priority": priority,
        }
        data = f"Drop Percentage: {drop_pct}%\n{cause}"

        cls._push_ntfy(headers=headers, data=data, type="ble")


    @classmethod
    def jam_ongoing(cls, seconds, priority="max"):
        """This will push a repeat alert every --jam interval while a jam is active"""

        headers = {
            "Title": "Bluetooth Jamming Ongoing",
            "Priority": priority,
        }
        data = f"Jamming still active — {_dur(seconds)} and counting"

        cls._push_ntfy(headers=headers, data=data, type="ble")


    # ==========
    #  HEARTBEAT
    # ==========
    @classmethod
    def hourly_summary(cls):
        """This will push a periodic area summary — ble / aps / clients / jam"""


        ble     = Variables.ble_current
        aps     = sum(1 for ap in list(Variables.live_map_wifi.values()) if time.time() - ap.get("last_seen", 0) <= Variables.wifi_ap_stale)
        clients = sum(1 for ap in list(Variables.live_map_wifi.values()) for c in list(ap.get("clients", {}).values()) if c.get("status") in ("online", "idle"))
        minutes = int((time.time() - Variables.time_without_incidents) / 60)

        jam = "JAMMED" if Variables.jammed else "clear"

        headers = {
            "Title": f"Hourly Status — {jam}",
            "Priority": "high" if Variables.jammed else "low",
        }
        data = f"BLE: {ble}   APs: {aps}   Clients: {clients}\nJam: {jam}   {minutes} min without incidents"

        cls._push_ntfy(headers=headers, data=data, type="ble")


    @classmethod
    def start_hourly(cls):
        """This will spawn the hourly summary thread (only if an ntfy path is set)"""


        if not (Variables.ntfy_ble_path or Variables.ntfy_wifi_path): return

        def worker():

            while True:
                time.sleep(Variables.ntfy_hourly)
                cls.hourly_summary()

        threading.Thread(target=worker, args=(), daemon=True).start()
        console.print(f"[bold green][+] Successfully started hourly NTFY summary!")


    @classmethod
    def _push_ntfy(cls, headers, data, type="ble"):
        """This will be used to push notifications to a server to view via (mainly) phone"""
        
        
        if type   == "wifi": ntfy_path = Variables.ntfy_wifi_path
        elif type == "ble":  ntfy_path = Variables.ntfy_ble_path
        else: return False

        if not ntfy_path: return False

        url = f"https://ntfy.sh/{ntfy_path}"

        try:

            response = requests.post(url=url, headers=headers, data=data.encode("utf-8"))

            code = response.status_code
            
            """
            For rate limiting:
            code":42908
            error":"limit reached: daily message quota reached; increase your limits with a paid plan
            
            """

            if code in [200, 204]: console.print(f"[bold green][+] NTFY Notification successfully pushed!")
            else:                  console.print(f"[bold red][-] NTFY Notification Failed to push!")
        

        except Exception as e: console.print(f"[bold red][!] Exception error:[bold yellow] Failed to make requests.post!")




class Background_Threads:
    """This module will house background permanent running threads"""

    # CLASS VARIABLES
    hop = True
    channel = 0


    @classmethod
    def channel_hopper(cls, set_channel=False, verbose=False):
        """This method will be responsible for automatically hopping channels"""


        def hopper():

            iface    = Variables.iface_monitor
            delay    = Variables.wifi_hop_delay
            all_hops = Variables.wifi_hops


 
            if set_channel:
                cls.hop = False
                time.sleep(2)

                try:
                    subprocess.Popen(
                        [
                            "sudo",
                            "iw",
                            "dev",
                            iface,
                            "set",
                            "channel",
                            str(set_channel),
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True,
                    )

                except Exception as e:
                    console.print(f"[bold red]Exception Error:[bold yellow] {e}")

     
            while cls.hop:
                for channel in all_hops:
                    try:
              
                        subprocess.Popen(
                            [
                                "sudo",
                                "iw",
                                "dev",
                                iface,
                                "set",
                                "channel",
                                str(channel),
                            ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True,
                        )

                        cls.channel = channel
                        if verbose: console.print( f"[bold green]Hopping on Channel:[bold yellow] {channel}")

                        time.sleep(delay)

                    except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}")

        cls.hop = True
        threading.Thread(target=hopper, args=(), daemon=True).start()


    @staticmethod
    def set_monitor_mode(iface):
        """Put iface into monitor mode"""

        if Variables.iface_monitor:
            subprocess.run(f"sudo ip link set {iface} down; sudo iw dev {iface} set type monitor; sudo ip link set {iface} up", shell=True)


    @staticmethod
    def change_iface_mode(iface, mode=["managed", "monitor"], verbose=True):
        """This method will be resposnible for chaning iface mode"""

        # if mode == "monitor": return
        try:
            if mode == "monitor" or mode == 2:
                # os.system(f"sudo ip link set {iface} down; sudo iw dev {iface} type monitor; sudo ip link set {iface} up")

                subprocess.run(
                    ["sudo", "ip", "link", "set", f"{iface}", "down"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["sudo", "iw", "dev", f"{iface}", "set", "type", "monitor"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["sudo", "ip", "link", "set", f"{iface}", "up"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            elif mode == "managed" or mode == 1:
                subprocess.run(
                    ["sudo", "ip", "link", "set", f"{iface}", "down"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["sudo", "iw", "dev", f"{iface}", "set", "type", "managed"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["sudo", "ip", "link", "set", f"{iface}", "up"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            else:
                console.print(
                    "[bold red][-] non-valid choice picked for change_iface_mode!"
                )
                return False

            check = subprocess.run(
                ["iw", "dev", f"{iface}", "info"], capture_output=True, text=True
            )
            if (
                "type monitor" in check.stdout.lower()
                or "type managed" in check.stdout.lower()
            ):
                console.print(
                    f"[bold green][+] Successfully changed iface_mode --> {mode}!"
                )

        except Exception as e:
            console.print(e)

        finally:
            console.print("[bold red] Ctrl + c x2 == EXIT\n")



class TTS():
    """This class will be reponsible for holding tts logic"""


    speaking = False



    @classmethod
    def _fixes(cls):
        """This will have a list of post and pre words to use in hte watcher to switch up what is said"""


        words = [
            ("ayo listen bro",    "you already know"),
            ("yo peep this",      "we locked in"),
            ("peep this",         "on god"),
            ("yo real quick",     "we straight"),
            ("ayo bari",          "we good"),
            ("yo we locked in",   "hold it down"),
            ("listen up bro",     "we up"),
            ("yo check it",       "no cap"),
            ("pay attention bro", "stay up bro"),
            ("ayo",               "we watching"),
            ("yo bro",            "on god bro"),
            ("yo peep it",        "we on watch"),
            ("lowkey heads up",   "keep it locked"),
            ("check this out",    "we still up"),
            ("yo listen",         "aint nothin slidin past"),
            ("real quick bro",    "we on point"),
            ("yo peep game",      "no cap bro"),
            ("yo bro",            "we posted"),
            ("yo dig this",       "on my mama"),
            ("yo peep it",        "we watchin the block"),
            ("ayo fam",           "you know how we rock"),
            ("heads up bro",      "we solid"),
            ("yo its ya boy yoda","we out here watchin"),
            ("pay attention",     "stay dangerous bro"),
            ("yo quick one",      "keep ya head on a swivel"),
            ("",                  "we straight up top"),
            ("",                  "on my mama"),
            ("",                  "deadass"),
            ("",                  "you already know"),
            ("",                  ""),
        ]


        word = random.choice(words)

        return word




    @classmethod
    def _message(cls, kind, **kw):
        """This will build the spoken line for a given event so its all in one place"""


        if kind == "deauth":   return f"Warning: WiFi deauthentication attack on channel {kw.get('channel') or 'unknown'} from the ap of: {kw.get('ap_ssid') or 'unknown'}"
        if kind == "ap_count": return f"Attention: WiFi access point count has {kw.get('word')}"
        if kind == "boot":     return "Yoda, made by NSM Bari, now up and running!"

        if kind == "jam":
            s = int(kw.get("seconds", 0))
            if s < 5: return "Attention: Bluetooth jamming attack detected!"
            return f"Warning: Bluetooth jamming ongoing for {_dur(s)}"

        if kind == "status":
            pre, post         = cls._fixes()
            ble, aps, clients = kw.get("ble", 0), kw.get("aps", 0), kw.get("clients", 0)
            core              = f"Area status: {ble} bluetooth devices, {aps} access points and {clients} clients. It has been {_dur(kw.get('seconds', 0))} without incidents"
            return ". ".join(p for p in (pre, core, post) if p)

        return kw.get("say", "")



    @classmethod
    def _audio_env(cls):
        """Route root's audio to the real user's PipeWire session (sudo sets SUDO_UID)."""


        env = dict(os.environ)
        uid = env.get("SUDO_UID")
        if uid: env["XDG_RUNTIME_DIR"] = f"/run/user/{uid}"
        return env



    @classmethod
    def speak(cls, say=None, kind=None, **kw):
        """This will speak one line, or skip if already speaking. Returns True if it spoke"""


        if kind: say = cls._message(kind, **kw)
        if not say: return False

        with Variables.LOCK:
            if cls.speaking: return False
            cls.speaking = True


        def worker():

            try:
                with wave.open(TTS_WAV, "w") as wav: cls.voice.synthesize_wav(say, wav)
                console.print(f"[green][+] Speaking:[yellow] {say}")
                subprocess.run(["pw-play", f"{TTS_WAV}"], env=cls._audio_env(), stderr=subprocess.DEVNULL)

            except Exception as e: console.print(f"[bold red][!] Exception Error:[yellow] {e}")

            finally: cls.speaking = False


        threading.Thread(target=worker, args=(), daemon=True).start()
        return True



    @classmethod
    def _watcher(cls):
        """This runs forever and speaks whatever the state calls for — one at a time, no overlap"""


        def worker():

            last_status = time.time()

            while True:

                time.sleep(.1)

                if Variables.jammed:
                    seconds = time.time() - Variables.time_without_incidents
                    if cls.speak(kind="jam", seconds=seconds) and Variables.jam_notify:
                        Notifications.jam_ongoing(seconds=seconds)

                elif time.time() - last_status >= Variables.watcher_calm:
                    ble     = Variables.ble_current
                    aps     = sum(1 for ap in list(Variables.live_map_wifi.values()) if time.time() - ap.get("last_seen", 0) <= Variables.wifi_ap_stale)
                    clients = sum(1 for ap in list(Variables.live_map_wifi.values()) for c in list(ap.get("clients", {}).values()) if c.get("status") in ("online", "idle"))
                    seconds = time.time() - Variables.time_without_incidents
                    if cls.speak(kind="status", ble=ble, aps=aps, clients=clients, seconds=seconds):
                        last_status = time.time()


        threading.Thread(target=worker, args=(), daemon=True).start()
        console.print(f"[bold green][+] Successfully started Watcher thread!")




    @classmethod
    def init(cls):
        """This will be used to initalize voice module for Text --> Speech"""



        try:

            cls.voice = PiperVoice.load(MODEL)

            cls._watcher()
            console.print(f"[bold green][+] Successfully loaded Voice Module!")
 
            return True


        except Exception as e: console.print(f"[bold red][!] Exception Error:[yellow] {e}"); return False






# BELOW IS FOR TESTING 
if __name__ == "__main__":

    TTS.init()
    Variables.jammed = True

    while True: time.sleep(1)
