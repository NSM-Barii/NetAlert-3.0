# NEW FOLDER FOR ATTACK MODULES


# UI IMPORTS
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.console import Console
import pyfiglet

console = Console()


# NETWORK IMPORTS
import socket, requests, ipaddress
from scapy.all import Ether, ARP, IP, srp


# ETC IMPORTS
import time






class ARP_Poison():
    """This class will hold logic responsible for performing a ARP Poison Attack"""

    
    # DEVICES
    devices = []
    RUN = True
    DELAY = 10


    # COLORS
    c1 = "bold red"
    c2 = "bold blue"
    c3 = "bold yellow"
    c4 = "bold green"




    @classmethod
    def subnet_scanner(cls, subnet, verbose=0):
        """This will continously scan the subnet for avaliable devices"""


        pkt = Ether(dst="ff:ff:ff:ff:ff:f") / ARP(dst="ff:ff:ff:ff:ff:ff", pdst=str(subnet))

        response = srp(pkt, store=0, verbose=verbose)[0]

        for sent, recieved in response:

            target_mac = recieved.hwsrc
            target_ip = recieved.psrc

            # APPEND TO LIST
            if target_ip not in cls.devices:

                cls.devices.append(target_ip)
            

                # VERBOSE
                console.print(f"Device Found  -  IP: {target_ip} - Mac: {target_mac}")
    


    @classmethod
    def loop_scans(cls):
        """This module will be responsibe for looping ARP scan"""


        while cls.RUN:


            ARP_Poison.loop_scans()

            time.sleep(cls.DELAY)


     





