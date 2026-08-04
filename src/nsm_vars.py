# THIS WILL HOUSE MULTI-MODULE VARS (post yoda-jr)


# IMPORTS
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
#from mcp.server.fastmcp import FastMCP
import threading, queue, time



# MONITOR METHODS
"""
monitor_bluetooth
monitor_deauth
monitor_evil_twin
monitor_ssid_count



"""

# Kodak: https://www.youtube.com/watch?v=accWa7GGCd4&list



class Variables():
    """This will house multi module vars"""



    EVENT_TIMES = {}
    EVENT_QUEUE = queue.Queue()
    LAST_EVENT_TIME = 0
    EVENT_COOLDOWN = 5


    @classmethod
    def push_event(cls, text):
        """
        Push event to queue for voice notifications.
        Voice agent will pick this up and speak it via session.say()

        Args:
            text: Event message to be spoken
        """

        now = time.time()
        last = cls.EVENT_TIMES.get(text, 0)

        if now - last < cls.EVENT_COOLDOWN:
            return

        cls.EVENT_TIMES[text] = now
        cls.EVENT_QUEUE.put(text)




    # CONSTANTS
    tui   = False
    console = Console()
    #mcp  = FastMCP("Yoda")
    LOCK = threading.RLock()


    # RICH VARS
    panel = Panel(renderable="Developed by NSM Barii", style="bold yellow", border_style="bold red", expand=False)
    table = Table(title="Developed by NSM Barii", style="bold purple", border_style="bold red", title_style="bold purple", header_style="bold purple")
    refresh_per_second = 1
    
    
    obfuscate     = False
    iface_managed = False
    subnet    = "192.168.1.0/24"
    ip_router = "192.168.1.1"
    ip_local  = False
    verbose   = False


    # TTS
    jammed = False
    esp_ip = False   # set to an ESP32 LED-server IP to enable the LED output (parked until then)
    tts_cooldown = 30
    watcher_calm = 60 * 30
    watcher_jam  = 60 * 3
    jam_notify   = False
    time_without_incidents = time.time()

    

    # MONITORING VARS
    iface_monitor = "wlan1"  # FOR MONITOR MODE
    ble_adapter   = False    # BlueZ hci name for BLE, e.g. hci1 (False = system default)
    
    ntfy_ble_path  = False
    ntfy_wifi_path = False
    ntfy_hourly          = 60 * 60
    notify_client_events = False
    tts_interval         = 600
    
    pct_set_unstable = 25
    pct_set_drop     = 35

    wifi_client_idle    = 120
    wifi_client_offline = 600
    wifi_ap_stale       = 60

    wifi_hop_delay = .25
    wifi_hops      = [1, 6, 11, 36, 40, 44, 48, 149, 153, 157, 161]
    ble_scan_duration = 5

    presets = {
        "2.4": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "5":   [36, 40, 44, 48, 149, 153, 157, 161],
        "all": [1, 6, 11, 36, 40, 44, 48, 149, 153, 157, 161]
    }


 
    
    # END
    lan_current = 0
    lan_max     = 0
    lan_min     = 0

    ble_current  = 0
    ble_max      = 0
    ble_min      = float("inf")

    wifi_current = 0
    wifi_max     = 0
    wifi_min     = float("inf")

    
    live_map_lan  = {}
    live_map_bt   = {}
    live_map_wifi = {}

    




    @classmethod
    def Attacks(cls):
        """This will house all the different attacks of which we are going to do"""

            
        # =============================
        # WiFI/BLE BACKGROUND SCANNING
        # =============================
        global_ble_devices  = 0
        global_ssids         = 0

        
        
        # ================================
        # WiFi  //   MONITOR MODE ATTACKS
        # ================================


        # DEFAULT
        timeout = 15
        channel = 6 # OR 6

        # WAR DRIVING
        mode = 1 # AP's ONLY == 1 else 2 == FOR CLIENTS AND NON BEACON FRAMES

        # EVIL TWIN // BEACON FLOOOOD
        portal_num = 1    

        # DEAUTH // CLIENT SNIFFER
        mac_src    = None
        mac_dst    = None
        mac_client = None  # SINGLE CLIENT DEAUTH

        inter    = None
        loop     = None
        count    = None
        realtime = None

        reasons = [4,5,7,15]



        # ===============
        #  Bluetooth/BLE
        # ===============


        live_map  = {}
        war_drive = {}
        unstable_devices = 0
        server_ip = False

