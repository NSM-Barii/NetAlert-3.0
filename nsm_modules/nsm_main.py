# THIS MODULE WILL BE DIFFERENT THEN PREVIOUS NSM_MAIN <-- THIS ONE WILL REPLACE NSM_UI



# IMPORTS
import scapy, manuf, ipaddress
import requests, rich, pathlib, pyfiglet, pandas, numpy, gtts, pyttsx3, threading, time
from datetime import datetime
from rich.console import Console


# NSM IMPORTS
from nsm_files import Push_Network_Status, File_Handling
from nsm_utilities import Utilities, Connection_Handler
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
                
                # GET CONN STATUS
                  if Connection_Handler.get_conn_status():


                        # GET IFACE
                        iface = Utilities.get_valid_interface()


                        # GET SUBNET
                        subnet = Utilities.get_subnet()


                        # GET UI
                        ui = Utilities.gui_or_cli()


                        # GET LOCAL IP
                        local_ip = Connection_Handler.get_local_ip()


                        # CLEANSE JSON
                        Push_Network_Status.push_device_info()


                        # TIMESTAMP IT
                        Utilities.get_time_stamp(ui=ui)


                        # START SUMMARY COUNT
                        Push_Network_Status.get_network_summary()
                        

                        # START NETWORK SCANER
                        Network_Scanner.main(ui=ui, iface=iface, subnet=subnet)


                        # START NETWORK SNIFFER
                        #Network_Sniffer.main(ui=ui, iface=iface)


                        # RUN FRONT END GUI
                        Server.begin_web_server(iface=iface, local_ip=local_ip)



                        while True:
                              pass




          except Exception as e:
            print(f"Exception Error: {e}")



if __name__ == "__main__":
     Main.run()
