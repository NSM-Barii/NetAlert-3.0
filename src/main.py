# THIS WILL BE THE START OF SOMETHING GREAT // _archive holds old concept

# UI IMPORTS
from rich.panel import Panel



# ETC IMPORTS
import threading, time, sys, argparse


# NSM IMPORTS
from nsm_vars import Variables
from nsm_tui import TUI, CLI
from nsm_database import Background_Threads
#import nsm_server_mcp
# import nsm_voice_agent


# CONSTANTS
console = Variables.console



def main():
    """This will be used to start main program"""

    data = (
        "[bold cyan]  Y O D A[/bold cyan]"
        "\n[dim]  Passive RF Monitoring System[/dim]"
        "\n\n[bold white]  Monitors[/bold white]"
        "\n[bold blue]  •[/bold blue] [white]Bluetooth/BLE[/white]   [dim]— nearby devices, vendors, signal strength[/dim]"
        "\n[bold green]  •[/bold green] [white]WiFi APs[/white]       [dim]— access points, channels, client counts[/dim]"
        "\n[bold yellow]  •[/bold yellow] [white]WiFi Clients[/white]   [dim]— devices connecting to nearby networks[/dim]"
        "\n\n[bold white]  Usage[/bold white]"
        "\n  [dim]python main.py [/dim][cyan]-i wlan1[/cyan]"
        "\n  [dim]python main.py [/dim][cyan]-i wlan1 -ntfy my-topic-123[/cyan]"
        "\n\n[dim]  Made by NSM Barii[/dim]"
    )

    

    panel = Panel(renderable=data, style="bold red", border_style="bold red", padding=(1, 2))


    parser = argparse.ArgumentParser(
        add_help=False,
        description="Yoda — Passive RF monitoring. Tracks BLE devices, WiFi APs, and clients in your area."
    )

    parser.add_argument("-i",    metavar="IFACE",      help="Monitor mode interface (default: wlan1)")
    parser.add_argument("--bu", type=int, default=None,  help="BLE unstable device threshold (default: 25)")
    parser.add_argument("--bd", type=int, default=None,  help="BLE drop score threshold (default: 25)")
    parser.add_argument("-ntfy", metavar="TOPIC",      help="ntfy topic for push notifications (e.g. my-topic-123)")
    parser.add_argument("--help", "-h", action="store_true",  help="Show this help message")
    parser.add_argument("--obs",  action="store_true", help="Obfuscate MACs and SSIDs in the TUI")


    args = parser.parse_args()


    if args.help: 
        CLI._print_welcome()
        parser.print_help()
        return False

    # CLI OVERRIDES  ——  applied BEFORE CLI.main() so each becomes the default shown in the interactive prompt
    if args.obs:               Variables.obfuscate        = True
    if args.i    is not None:  Variables.iface_monitor    = args.i
    if args.ntfy is not None:  Variables.ntfy_ble_path    = Variables.ntfy_wifi_path = args.ntfy
    if args.bu   is not None:  Variables.pct_set_unstable = args.bu
    if args.bd   is not None:  Variables.pct_set_drop     = args.bd


    CLI.main()
    Background_Threads.set_monitor_mode(iface=Variables.iface_monitor)
    TUI().run()






if __name__ == "__main__": main()
