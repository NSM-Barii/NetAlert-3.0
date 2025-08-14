# THIS MODULE WILL BE DIFFERENT THEN PREVIOUS NSM_MAIN <-- THIS ONE WILL REPLACE NSM_UI



# IMPORTS
import scapy, manuf, ipaddress
import requests, rich, pathlib, pyfiglet, pandas, numpy, gtts, pyttsx3, threading, time
from datetime import datetime
from rich.console import Console


# NSM IMPORTS
from nsm_files import Push_Network_Status
from nsm_utilities import Utilities
from nsm_network_scanner import Network_Scanner
from nsm_network_scanner import Network_Sniffer
from nsm_server import Server


# CONSTANTS
console = Console()




class Main():
    """This will spawn multi module logic"""

    
    def __init__(self):
           pass
    


    @classmethod
    def run(cls):
          """Start here"""


          try:


                # GET IFACE
                iface = Utilities.get_valid_interface()


                # GET SUBNET
                subnet = Utilities.get_subnet()


                # IF THAT WORKS PROCEED
                ui = Utilities.gui_or_cli()


                # TELL
                time_stamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
                console.print(f"\n{ui.upper()} Mode Activated  -  Timestamp: {time_stamp}", style="bold green")


                # START SUMMARY COUNT
                threading.Thread(target=Push_Network_Status.get_network_summary, args=(5, False), daemon=True).start()
                console.print("[bold red][+][bold yellow] Background Thread 1 started")
                


                # START NETWORK SCANER
                Network_Scanner.main(ui=ui, iface=iface, subnet=subnet)


                # START NETWORK SNIFFER
                #Network_Sniffer.main(ui=ui, iface=iface)


                # RUN FRONT END GUI
                time.sleep(0.2)
                Server.begin_web_server()



                while True:
                  pass




          except Exception as e:
            print(f"Exception Error: {e}")



if __name__ == "__main__":
     Main.run()
