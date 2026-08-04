# THIS MODULE WILL HOST THE WEB DASHBOARD


# WEB IMPORTS
from http.server import SimpleHTTPRequestHandler, HTTPServer
from functools import partial


# ETC IMPORTS
from pathlib import Path
import json, threading, time


# NSM IMPORTS
from nsm_vars import Variables
from nsm_detector import Detector


# CONSTANTS
console  = Variables.console
GUI_PATH = Path(__file__).parent.parent / "gui"
BLE      = Detector.BLE



def _mask_mac(mac):
    """This will keep the vendor OUI and hide the unique half"""

    if not mac or mac.count(":") != 5: return "xx:xx:xx:xx:xx:xx"
    return mac[:8] + ":xx:xx:xx"




class HTTP_Handler(SimpleHTTPRequestHandler):
    """This will handle dashboard requests"""


    def end_headers(self):
        """Never let the browser cache — the dashboard + /data must always be fresh"""

        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


    def do_GET(self):
        """Serve /data as live JSON, everything else as a static file from gui/"""


        if self.path == "/data":

            payload = json.dumps(self._snapshot()).encode()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
            return

        return super().do_GET()



    def _snapshot(self):
        """Read the live state -> a JSON-ready dict for the dashboard"""


        with Variables.LOCK:


            obf = Variables.obfuscate


            # BLE DEVICES  (list() -> snapshot so a mutating monitor thread can't change size mid-iteration)
            ble_devices = []
            for mac, dev in list(Variables.live_map_bt.items()):

                data = dev.get("data", {})
                rssi = data.get("rssi")
                if rssi is None and dev.get("rssi_list"): rssi = dev["rssi_list"][-1]

                ble_devices.append({
                    "mac":    _mask_mac(mac) if obf else mac,
                    "name":   data.get("name")   or "",
                    "vendor": data.get("vendor") or "",
                    "rssi":   rssi,
                    "status": dev.get("status", "stable"),
                    "seen":   dev.get("seen_cycles", 0),
                })


            # WIFI APs + CLIENTS  (fresh APs + present clients only, so the table matches the counts)
            wifi_aps     = []
            client_count = 0
            now          = time.time()
            for bssid, ap in list(Variables.live_map_wifi.items()):

                if now - ap.get("last_seen", 0) > Variables.wifi_ap_stale: continue

                clients       = [{"mac": _mask_mac(m) if obf else m, "status": c.get("status", "online"), "vendor": c.get("vendor") or "", "rssi": c.get("rssi")} for m, c in list(ap.get("clients", {}).items()) if c.get("status") in ("online", "idle")]
                client_count += len(clients)

                ssid = ap.get("ssid") or ""

                wifi_aps.append({
                    "bssid":   _mask_mac(bssid) if obf else bssid,
                    "ssid":    ("•••" if ssid else "") if obf else ssid,
                    "channel": ap.get("channel"),
                    "rssi":    ap.get("rssi"),
                    "vendor":  ap.get("vendor") or "",
                    "clients": clients,
                })


            return {
                "ble": {
                    "count":        len(Variables.live_map_bt),
                    "jammed":       Variables.jammed,
                    "drop_pct":     getattr(BLE, "prev_drop_pct", 0),
                    "unstable_pct": getattr(BLE, "prev_unstable_pct", 0),
                    "devices":      ble_devices,
                },
                "wifi": {
                    "ap_count":     len(wifi_aps),
                    "client_count": client_count,
                    "aps":          wifi_aps,
                },
            }



    def log_message(self, format, *args): pass   # suppress request logs




class Web_Server():
    """This will launch the web server instance"""


    @classmethod
    def _server(cls, port):
        """Serve the dashboard + /data endpoint from gui/"""


        handler = partial(HTTP_Handler, directory=str(GUI_PATH))
        server  = HTTPServer(("", port), handler)

        console.print(f"[bold green][+] Dashboard:[bold yellow] http://localhost:{port}")

        server.serve_forever()



    @classmethod
    def init(cls, port=8080):
        """Start the web server on a daemon thread"""


        threading.Thread(target=cls._server, args=(port,), daemon=True).start()
