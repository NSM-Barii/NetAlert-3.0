# THIS FILE WILL BE USED TO CREATE SMOOTH USER INTERFACES


# TUI IMPORTS
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Header, Footer, Label, DataTable, Tree, TabbedContent, TabPane
from textual.containers import Horizontal


# ETC IMPORTS
import time, pyfiglet, subprocess, os, re
from datetime import datetime

# NSM IMPORTS
from nsm_vars import Variables
from nsm_monitor import Monitor_Runner


# CONSTANTS
console = Variables.console
re_mac  = re.compile(r"((?:[0-9a-fA-F]{2}:){2}[0-9a-fA-F]{2})(?::[0-9a-fA-F]{2}){3}")


class TUI(App):

    CSS = """
    #stats {
        height: 3;
        width: auto;
        content-align: left middle;
        padding: 0 2;
        border: round grey;
    }
    TabbedContent { height: 1fr; }
    TabPane       { height: 1fr; }
    #up           { height: 1fr; }
    #ble          { width: 1fr; border: round red;   }
    #wifi         { width: 1fr; border: round green; }
    """

    def compose(self):
        """This will initialize the TUI"""


        yield Header(id="yoda")
        yield Label("BLE: 0  |  APs: 0  |  Clients: 0", id="stats")

        with TabbedContent():
            with TabPane("Dashboard"):
                with Horizontal(id="up"):
                    yield RichLog(id="ble",  markup=True)
                    yield RichLog(id="wifi", markup=True)

            with TabPane("BLE Devices"):
                yield DataTable(id="ble_table", cursor_type="row")

            with TabPane("WiFi APs"):
                yield DataTable(id="ap_table", cursor_type="row")

            with TabPane("WiFi Tree"):
                yield Tree("Access Points", id="wifi_tree")

            with TabPane("Channels"):
                yield DataTable(id="ch_table", cursor_type="row")

        yield Footer()


    def on_mount(self):
        """This will add to said initialized TUI"""

        self.query_one("#ble",  RichLog).border_title = "Bluetooth/BLE"
        self.query_one("#wifi", RichLog).border_title = "WiFi"

        ble_table = self.query_one("#ble_table", DataTable)
        _, self._ck_ble_rssi, _, _, _, _, self._ck_ble_first, self._ck_ble_session, self._ck_ble_status = ble_table.add_columns(
            "#", "RSSI", "MAC", "Name", "Vendor", "Manufacturer", "First Seen", "Session", "Status"
        )

        ap_table = self.query_one("#ap_table", DataTable)
        _, self._ck_ap_rssi, _, _, _, _, self._ck_ap_clients, self._ck_ap_first, self._ck_ap_session, self._ck_ap_status = ap_table.add_columns(
            "#", "RSSI", "SSID", "BSSID", "Vendor", "Channel", "Clients", "First Seen", "Session", "Status"
        )

        self.query_one("#wifi_tree", Tree).root.expand()

        ch_table = self.query_one("#ch_table", DataTable)
        _, self._ck_ch_aps, self._ck_ch_clients, self._ck_ch_bar = ch_table.add_columns(
            "Channel", "APs", "Clients", "Congestion"
        )

        self._ble_rows      = {}
        self._ble_first_ts  = {}
        self._ap_rows       = {}
        self._ap_first_ts   = {}
        self._ap_branches   = {}
        self._ch_rows       = {}

        Variables.tui = self
        Monitor_Runner.main()


    def push_data(self, id, data):
        """This will be used to push data"""

        if Variables.obfuscate:
            data = re_mac.sub(r"\1:xx:xx:xx", data)
            from nsm_monitor import Monitor_WiFi
            for ap in Monitor_WiFi.live_map.values():
                ssid = ap.get("ssid")
                if ssid and ssid in data:
                    data = data.replace(ssid, ssid[:3] + "*" * 5) #(len(ssid) - 3))
        self.query_one(str(id), RichLog).write(data)


    def update_stats(self, ble: int, wifi_aps: int, wifi_clients: int):
        """This will be used to update stats"""

        self.query_one("#stats", Label).update(f"[bold red]BLE: {ble}[/bold red]  [dim]|[/dim]  [bold green]APs: {wifi_aps}[/bold green]  [dim]|[/dim]  [bold blue]Clients: {wifi_clients}[/bold blue]")


    @staticmethod
    def _fmt_session(start_ts):
        """This will be used to get time, this lowkey makes sense after looking at it for a while."""

        elapsed = int(time.time() - start_ts)
        h, rem  = divmod(elapsed, 3600)
        m, s    = divmod(rem, 60)
        if h:    return f"{h}h {m}m"
        if m:    return f"{m}m {s}s"
        return f"{s}s"


    def upsert_ble(self, mac, vendor, manuf, name, rssi, status="online"):
        """append ble device"""


        table = self.query_one("#ble_table", DataTable)
        color = "green" if status == "online" else "dim"

        if mac in self._ble_rows:
            key     = self._ble_rows[mac]
            session = self._fmt_session(self._ble_first_ts[mac])
            try: table.update_cell(key, self._ck_ble_rssi,    str(rssi))
            except: pass
            try: table.update_cell(key, self._ck_ble_session, session)
            except: pass
            try: table.update_cell(key, self._ck_ble_status,  status)
            except: pass
        else:
            now       = time.time()
            first_str = datetime.now().strftime("%H:%M:%S")
            self._ble_first_ts[mac] = now
            num = len(self._ble_rows) + 1
            display_mac = ":".join(mac.split(":")[:3]) + ":xx:xx:xx" if Variables.obfuscate else mac
            row = (str(num), str(rssi), f"[{color}]{display_mac}", name or "-", vendor or "-", manuf or "-", first_str, "0s", status)
            self._ble_rows[mac] = table.add_row(*row)


    def upsert_ap(self, bssid, ssid, vendor, channel, rssi, clients, status="online"):
        """append wifi ap"""


        table = self.query_one("#ap_table", DataTable)
        color = "green" if status == "online" else "dim"
        if bssid in self._ap_rows:
            key     = self._ap_rows[bssid]
            session = self._fmt_session(self._ap_first_ts[bssid])
            try: table.update_cell(key, self._ck_ap_rssi,    str(rssi))
            except: pass
            try: table.update_cell(key, self._ck_ap_clients, str(clients))
            except: pass
            try: table.update_cell(key, self._ck_ap_session, session)
            except: pass
            try: table.update_cell(key, self._ck_ap_status,  status)
            except: pass
        else:
            now       = time.time()
            first_str = datetime.now().strftime("%H:%M:%S")
            self._ap_first_ts[bssid] = now
            num = len(self._ap_rows) + 1
            display_ssid  = ssid[:3] + "*" * (len(ssid) - 3) if Variables.obfuscate else ssid
            display_bssid = ":".join(bssid.split(":")[:3]) + ":xx:xx:xx" if Variables.obfuscate else bssid
            row = (str(num), str(rssi), f"[{color}]{display_ssid}", display_bssid, vendor or "-", str(channel), str(clients), first_str, "0s", status)
            self._ap_rows[bssid] = table.add_row(*row)


    def add_ap_to_tree(self, bssid, ssid, rssi):
        """This will ad an ap to a tree"""

        tree          = self.query_one("#wifi_tree", Tree)
        display_ssid  = ssid[:3] + "*" * 5 if Variables.obfuscate else ssid
        display_bssid = ":".join(bssid.split(":")[:3]) + ":xx:xx:xx" if Variables.obfuscate else bssid
        branch = tree.root.add(f"[bold green]{display_ssid}[/bold green]  [dim]{display_bssid}[/dim]  [cyan]{rssi}dBm[/cyan]", expand=True)
        self._ap_branches[bssid] = branch


    def add_client_to_tree(self, bssid, mac, vendor):
        """This will add clients to the tree"""

        if bssid not in self._ap_branches: return
        display_mac = ":".join(mac.split(":")[:3]) + ":xx:xx:xx" if Variables.obfuscate else mac
        self._ap_branches[bssid].add_leaf(f"[yellow]{display_mac}[/yellow]  [dim]{vendor or 'Unknown'}[/dim]")


    def upsert_channel(self, channel, aps, clients):
        """This will update the channel congestion table"""

        table = self.query_one("#ch_table", DataTable)
        bar   = "█" * aps + "░" * max(0, 10 - aps)

        if channel in self._ch_rows:
            key = self._ch_rows[channel]
            try: table.update_cell(key, self._ck_ch_aps,     str(aps))
            except: pass
            try: table.update_cell(key, self._ck_ch_clients, str(clients))
            except: pass
            try: table.update_cell(key, self._ck_ch_bar,     bar)
            except: pass
        else:
            self._ch_rows[channel] = table.add_row(str(channel), str(aps), str(clients), bar)



class CLI():
    """This will be used to get custom vars from user before transitioning to the TUI"""



    @classmethod
    def _clear_screen(cls):
        """This is soley used to clear the screen and make a nice sexy terminal"""


        try:


            if   os.name == "nt":    subprocess.run("cls",   shell=True)
            elif os.name == "posix": subprocess.run("clear", shell=True)
        
        except Exception as e: console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")


    @classmethod
    def _print_welcome(cls):
        """This will be used to print Yoda"""
        
        l = "=" * 50
        text = (
            f"[yellow]{l}[/yellow]"
            "\n[dim]Passive RF monitoring  •  BLE  •  WiFi  •  Spectrum[/dim]"
            f"\n[yellow]{l}[/yellow]"
        )
        art = pyfiglet.figlet_format(text="Yoda", font="dos_rebel")
        console.print(f"\n{art}", style="bold green")
        console.print(text)
        print("\n\n")


    
    @classmethod
    def _check_vars(cls):
        """This will check def vars, if not true then summon assign"""

        
        # FOR NOW THIS WILL RETURN TRUE INDEFINETLY TO CONTINUE RUNNING CLI ALL THE TIME
        return True


        if not Variables.ntfy_ble_path: 
            return False
        
        if Variables.ntfy_wifi_path:
            return False
    

    @classmethod
    def _default_vars(cls):
        """This will print the default vars as the user can just keep tapping enter"""

        c1 = "dim white"
        c4 = "cyan"

        stats = (
            f"[{c1}] [+] WiFi Interface:[/{c1}]    [{c4}]{Variables.iface_monitor}[/{c4}]"
            f"\n[{c1}] [+] NTFY BLE path:[/{c1}]     [{c4}]{Variables.ntfy_ble_path}[/{c4}]"
            f"\n[{c1}] [+] NTFY WiFi path:[/{c1}]    [{c4}]{Variables.ntfy_wifi_path}[/{c4}]"
            f"\n[{c1}] [+] Client idle:[/{c1}]       [{c4}]{Variables.wifi_client_idle}s[/{c4}]"
            f"\n[{c1}] [+] Client offline:[/{c1}]    [{c4}]{Variables.wifi_client_offline}s[/{c4}]"
            f"\n[{c1}] [+] BLE unstable pct:[/{c1}]  [{c4}]{Variables.pct_set_unstable}%[/{c4}]"
            f"\n[{c1}] [+] BLE drop pct:[/{c1}]      [{c4}]{Variables.pct_set_drop}%[/{c4}]"
            f"\n[{c1}] [+] WiFi Hops:[/{c1}]         [{c4}]{Variables.wifi_hops}[/{c4}]"
            f"\n[{c1}] [+] WiFi Hop Delay:[/{c1}]    [{c4}]{Variables.wifi_hop_delay}s[/{c4}]"
            f"\n[{c1}] [+] Verbose:[/{c1}]           [{c4}]{Variables.verbose}[/{c4}]"
            f"\n[{c1}] [+] Client ntfy:[/{c1}]     [{c4}]{Variables.notify_client_events}[/{c4}]"
            f"\n[{c1}] [+] TTS interval:[/{c1}]    [{c4}]{Variables.tts_interval}s[/{c4}]"
        )

        console.print(f"\n[dim]{'─' * 30}  Default Variables  {'─' * 30}[/dim]")
        console.print(stats)
        console.print(f"[dim]{'─' * 80}[/dim]\n")



    @classmethod
    def _set_vars(cls):
        """This will be used to set vars via RICH cli"""


        c5 = "cyan"

        p1 = "[+]"
        p2 = "[*]"

        
        #console.print("[bold purple]=" * 40) 
        iface = console.input(f"[{c5}]{p2} iface_monitor:[/{c5}] ")                     or Variables.iface_monitor

        wifi_hops      = console.input(f"[{c5}]{p2} wifi_hops:[/{c5}] ")                #or Variables.wifi_hops
        wifi_hop_delay = console.input(f"[{c5}]{p2} wifi_hop_delay:[/{c5}] ")           or Variables.wifi_hop_delay
 
        wifi_client_idle    = console.input(f"[{c5}]{p2} wifi_client_idle:[/{c5}] ")    or Variables.wifi_client_idle
        wifi_client_offline = console.input(f"[{c5}]{p2} wifi_client_offline:[/{c5}] ") or Variables.wifi_client_offline

        pct_set_unstable = console.input(f"[{c5}]{p2} pct_set_unstable:[/{c5}] ")       or Variables.pct_set_unstable
        pct_set_drop     = console.input(f"[{c5}]{p2} pct_set_drop:[/{c5}] ")           or Variables.pct_set_drop

        ntfy_ble_path  = console.input(f"[{c5}]{p2} ntfy_ble_path:[/{c5}] ")            or Variables.ntfy_ble_path
        ntfy_wifi_path = console.input(f"[{c5}]{p2} ntfy_wifi_path:[/{c5}] ")           or Variables.ntfy_wifi_path
        verbose              = console.input(f"[{c5}]{p2} verbose:[/{c5}] ")              or Variables.verbose
        notify_client_events = console.input(f"[{c5}]{p2} notify_client_events:[/{c5}] ") or Variables.notify_client_events
        tts_interval         = console.input(f"[{c5}]{p2} tts_interval (secs):[/{c5}] ")  or Variables.tts_interval
        #console.print("[bold purple]=" * 40)

        
        if not wifi_hops: wifi_hops = Variables.wifi_hops
        elif wifi_hops in Variables.presets: Variables.wifi_hops = Variables.presets[wifi_hops]


        Variables.iface_monitor       = iface
        Variables.wifi_hops           = wifi_hops
        Variables.wifi_hop_delay      = wifi_hop_delay
        Variables.ntfy_ble_path       = ntfy_ble_path
        Variables.ntfy_wifi_path      = ntfy_wifi_path
        Variables.wifi_client_idle    = wifi_client_idle
        Variables.wifi_client_offline = wifi_client_offline
        Variables.pct_set_unstable    = pct_set_unstable
        Variables.pct_set_drop        = pct_set_drop
        Variables.verbose              = True if verbose else False
        Variables.notify_client_events = True if notify_client_events else False
        Variables.tts_interval         = int(tts_interval)

    @classmethod
    def _print_vars(cls):
        """This will print out the vars vals"""


        c1 = "dim white"
        c4 = "cyan"

        stats = (
            f"[{c1}] [+] WiFi Interface:[/{c1}]    [{c4}]{Variables.iface_monitor}[/{c4}]"
            f"\n[{c1}] [+] NTFY BLE path:[/{c1}]     [{c4}]{Variables.ntfy_ble_path}[/{c4}]"
            f"\n[{c1}] [+] NTFY WiFi path:[/{c1}]    [{c4}]{Variables.ntfy_wifi_path}[/{c4}]"
            f"\n[{c1}] [+] Client idle:[/{c1}]       [{c4}]{Variables.wifi_client_idle}s[/{c4}]"
            f"\n[{c1}] [+] Client offline:[/{c1}]    [{c4}]{Variables.wifi_client_offline}s[/{c4}]"
            f"\n[{c1}] [+] BLE unstable pct:[/{c1}]  [{c4}]{Variables.pct_set_unstable}%[/{c4}]"
            f"\n[{c1}] [+] BLE drop pct:[/{c1}]      [{c4}]{Variables.pct_set_drop}%[/{c4}]"
            f"\n[{c1}] [+] WiFi Hops:[/{c1}]         [{c4}]{Variables.wifi_hops}[/{c4}]"
            f"\n[{c1}] [+] WiFi Hop Delay:[/{c1}]    [{c4}]{Variables.wifi_hop_delay}s[/{c4}]"
            f"\n[{c1}] [+] Verbose:[/{c1}]           [{c4}]{Variables.verbose}[/{c4}]"
            f"\n[{c1}] [+] Client ntfy:[/{c1}]       [{c4}]{Variables.notify_client_events}[/{c4}]"
            f"\n[{c1}] [+] TTS interval:[/{c1}]      [{c4}]{Variables.tts_interval}s[/{c4}]"
        )

        console.print(f"\n[dim]{'─' * 30}  Your Variables  {'─' * 30}[/dim]")
        console.print(stats)
        console.print(f"[dim]{'─' * 80}[/dim]\n")
    

    @classmethod
    def main(cls):
        """This will control cli var assignment"""
  
        
        cls._clear_screen()
        cls._print_welcome()
        cls._default_vars()
        if cls._check_vars(): cls._set_vars()
        cls._print_vars()
        
        console.input(f"\n[dim]  Press Enter to continue...[/dim] ")






if __name__ == "__main__":
    TUI().run()
