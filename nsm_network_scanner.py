# THIS MODULE WILL BE FOR LOCAL DEVICES DISCOVERY AND HANDLING



# UI IMPORTS
import pyfiglet
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()


# NETWORK IMPORTS
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, srp, Ether
import socket, requests


# ETC IMPORTS
from concurrent.futures import ThreadPoolExecutor
import threading, time
from datetime import datetime


# ML --> IMPORTS
import pandas as pd, numpy, sqlite3


# NSM IMPORTS
from nsm_utilities import Utilities
from nsm_network_sniffer import Network_Sniffer


# PREVENT RACE CONIDTIONS
LOCK = threading.Lock() 





class Network_Scanner():
    """This class will be responsible for finding local devices and keep tracking off there connection status"""


    def __init__(self):
        pass
    


    @classmethod
    def threader(cls, iface, target):
        """This method will be responsible for handling the --> subnet_scanner <-- method with parallism"""



        # START BACKGROUND ARP SCAN
        threading.Thread(target=Network_Scanner.subnet_scanner, args=(iface, ), daemon=True).start()
        console.print("[bold red][+][bold yellow] Thread 1 started")


        # START BACKGROUND PACKET SNIFFER
        threading.Thread(target=Network_Sniffer.main, args=(iface, console), daemon=True).start()
        console.print("[bold red][+][bold yellow] Thread 2 started")


        # VERBOSE OFF
        Network_Sniffer.verbose = False

        
        # ALLOW THREADS TO START
       # time.sleep(3)


        # NETWORK NODE STATUS
        panel = Panel(renderable=f"Packets Sniffed: 0  -  Online Nodes: 0  -  Offline Nodes: 0  -  NetAlert-3.0 by Developed NSM Barii", 
                      border_style="bold green", style="bold yellow",
                      title="Network Status", expand=False
                      )
        

        with Live(panel, console=console, refresh_per_second=4):


            # COLORS
            c1 = "bold green"
            c2 = "bold red"
            c3 = "bold purple"


            while cls.SNIFF:


                # UPDATE RENDERABLE 
                panel.renderable = (f"[{c2}]Packets Sniffed:[/{c2}] {(Network_Sniffer.total_packets)}   -  [{c2}]Online Nodes:[/{c2}] {len(cls.subnet_devices)}  -  [{c2}]Offline Nodes:[/{c2}] 0  -  [{c1}]NetAlert-3.0 by Developed NSM Barii")

            
    @classmethod
    def subnet_scanner(cls, iface, target="192.168.1.0/24", verbose=True):
        """This will perform a ARP scan"""


        # COLORS
        c1 = "bold red"
        c2 = "bold green"
        c3 = "bold yellow"
        

        while cls.SNIFF:

            arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(target))


            response = srp(arp, iface=iface, timeout=5, verbose=0)[0]
        


            for sent, recv in response:

                target_ip = recv.psrc
                target_mac = recv.hwsrc


                if target_ip not in cls.subnet_devices[0]:
                    

                    # MAKE A TUPLE
                    node = (target_ip, target_mac)
                    
                    # APPEND TO LIST
                    cls.subnet_devices.append(node)
                

                # ALERT THE USER
                console.print(f"[{c1}][+] [{c2}]Found Device:[/{c2}] {target_ip} [{c3}]<--->[/{c3}] {target_mac}")
        

            
            # NOW WAIT UNTIL NEXT SCAN
            time.sleep(cls.scan_delay)
        




    @classmethod
    def main(cls):
        """This will be responsible for performing class wide logic"""


        # SET VARS
        cls.SNIFF = True
        cls.scan_delay = 60
        cls.subnet_devices = []




        # GET IFACE
        iface = Utilities.get_interface()


        # PERFORM ARP SCAN
        Network_Scanner.threader(iface=iface, target="192.168.1.0/24")




# STRICTLY FOR MODULE WIDE TESTING
if __name__ == "__main__":

    use = 1
    

    if use:
        Network_Scanner.main()