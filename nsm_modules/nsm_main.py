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

                        # CLEAR SCREEN
                        Utilities.clear_screen()


                        # TESTING
                        from nsm_utilities import TTS
                        TTS.tts_def(letter="start")
                        TTS.tts_google(say="Welcome to NetAlert 3.0, a Intrusion Prevention System developed by NSM Bari")

                        # MAIN TITLE
                        Main.run_title()


                        # START PROGRAM ELAPSED TIME COUNTER
                        Connection_Handler.daily_update(time_start=time.time())


                        # GET IFACE
                        iface = Utilities.get_valid_interface()


                        # GET SUBNET
                        subnet = Utilities.get_subnet()


                        # GET LOCAL IP
                        local_ip = Connection_Handler.get_local_ip()


                        # GET UI
                        ui = Utilities.gui_or_cli()


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



                        #while True:
                            #  pass




          except Exception as e:
            print(f"Exception Error: {e}")
      
    

    @classmethod
    def run_title(cls, text="         Net\n      Alert", color="bold blue",font="bloody"):
         

         # COLORS
         c1 = "bold blue"
         c2 = "bold red"


         # BORDER SPACE
         console.print("\n\n\n")
      

         # CREATE PROGRAM STATS
         t1 = pyfiglet.figlet_format(text="          Net", font=font)
         t2 = pyfiglet.figlet_format(text="       Alert", font=font)
         console.print(t1, style=c1)
         console.print(t2, style=c2)


         # CREDITS
         console.print(
              f"\n      [{c1}]==========================================================================",
              f"\n      [{c2}]    ==================   Developed by NSM Barii   ==================== [/{c2}]",
              f"\n      [{c1}]=========================================================================="
              )

         
         # PROGRAM SPACE
         print("\n\n")

      



if __name__ == "__main__": 
     Main.run()
