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
from nsm_files import File_Handling


# PREVENT RACE CONIDTIONS
LOCK = threading.Lock() 





class Network_Scanner():
    """This class will be responsible for finding local devices and keep tracking off there connection status"""


    def __init__(self):
        pass




    @classmethod
    def subnet_scanner(cls, iface, target="192.168.1.0/24"):
        """This will perform a ARP scan"""


        arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(target))


        response = srp(arp, iface=iface)



        for sent, recv in response:

            target_ip = recv.psrc
            target_mac = recv.hwsrc


            if target_ip not in cls.subnet_devices:


                cls.subnet_devices.append(target_ip)
    




    @classmethod
    def main(cls):
        """This will be responsible for performing class wide logic"""


        # SET VARS
        cls.subnet_devices = []




        # GET IFACE
        iface = Utilities.get_interface()


