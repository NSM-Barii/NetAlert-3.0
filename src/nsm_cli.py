# THIS FILE HOUSES THE INTERACTIVE CLI SETUP  (runs before launch to collect user vars)


# ETC IMPORTS
import subprocess, os, pyfiglet


# NSM IMPORTS
from nsm_vars import Variables


# CONSTANTS
console = Variables.console



class CLI():
    """This will be used to get custom vars from user before launching the detection system"""



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
        iface       = console.input(f"[{c5}]{p2} iface_monitor:[/{c5}] ")               or Variables.iface_monitor
        ble_adapter = console.input(f"[{c5}]{p2} ble_adapter:[/{c5}] ")                 or Variables.ble_adapter

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
        elif wifi_hops in Variables.presets: wifi_hops = Variables.presets[wifi_hops]


        Variables.iface_monitor       = iface
        Variables.ble_adapter         = ble_adapter
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
    def main(cls, headless=False):
        """This will control cli var assignment"""


        cls._clear_screen()
        cls._print_welcome()
        cls._default_vars()
        if not headless and cls._check_vars(): cls._set_vars()
        cls._print_vars()

        if not headless: console.input(f"\n[dim]  Press Enter to continue...[/dim] ")
