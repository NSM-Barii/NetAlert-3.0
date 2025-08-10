# THIS MODULE WILL BE FOR LOCAL DEVICES DISCOVERY AND HANDLING



# UI IMPORTS
import pyfiglet
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()


# NETWORK IMPORTS
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, srp, Ether, sr1
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
from nsm_files import File_Handling


# PREVENT RACE CONIDTIONS
LOCK = threading.Lock() 





class Network_Scanner():
    """This class will be responsible for finding local devices and keep tracking off there connection status"""


    def __init__(self):
        pass
    


    @classmethod
    def controller(cls, iface, target):
        """This method will be responsible for handling the --> subnet_scanner <-- method with parallism"""



        # START BACKGROUND ARP SCAN
        threading.Thread(target=Network_Scanner.subnet_scanner, args=(iface, ), daemon=True).start()
        console.print("[bold red][+][bold yellow] Thread 1 started")


        # START BACKGROUND PACKET SNIFFER
       # threading.Thread(target=Network_Sniffer.main, args=(iface, console), daemon=True).start()
       # console.print("[bold red][+][bold yellow] Thread 2 started")


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
                panel.renderable = (f"[{c2}]Packets Sniffed:[/{c2}] 0   -  [{c2}]Online Nodes:[/{c2}] {cls.nodes_online}  -  [{c2}]Offline Nodes:[/{c2}] {cls.nodes_offline}   -  [{c1}]NetAlert-3.0 by Developed NSM Barii")
    

    @classmethod
    def subnet_scanner(cls, iface, target="192.168.1.0/24", verbose=True):
        """This will perform a ARP scan"""


        # COLORS
        c1 = "bold red"
        c2 = "bold green"
        c3 = "bold yellow"
        num = 0
        

        while cls.SNIFF:

            arp = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(target))


            response = srp(arp, iface=iface, timeout=5, verbose=0)[0]
        


            for sent, recv in response:

                target_ip = recv.psrc
                target_mac = recv.hwsrc


                if target_ip not in cls.subnet_devices:
                    

                    # MAKE A TUPLE
                    node = (target_ip, target_mac)
                    
                    # APPEND TO LIST
                    cls.subnet_devices.append(target_ip)
                

                    # ALERT THE USER
                    console.print(f"[{c1}][+] [{c2}]New Device:[/{c2}] {target_ip} [{c3}]<-->[/{c3}] {target_mac}")


                    # TRACK DEVICE CONNECTION STATUS
                    threading.Thread(target=Network_Scanner.node_tracker, args=(target_ip, ), daemon=True).start()
        

            
            # NOW WAIT UNTIL NEXT SCAN
            num += 1
            console.print(f"Loop #{num}", style="bold red")
            time.sleep(cls.scan_delay)
        

    @classmethod
    def node_tracker(cls, target_ip, timeout=5, verbose=0):
        """This method will be responsible for tracking node connection status"""


        # SET VARS
        online = False
        delay = 10

        # SET ONLINE NOW
        cls.nodes_online += 1
        first = True


        # COLORS
        c1 = "bold red"
        c2 = "bold green"
        c3 = "bold yellow"
        c4 = "bold purple"



        # START THE RATE LIMITER
        threading.Thread(target=Network_Scanner.rate_limiter, args=(target_ip, ), daemon=True).start()



        # CREATE PING 
        ping = IP(dst=target_ip) / ICMP()
        

        # LOOP 
        while cls.SNIFF:

            
            try:

                # GET RESPONSE
                response = sr1(ping, timeout=timeout, verbose=verbose)


                
                # NOW ONLINE
                if response and online==False:


                    # TALK
                   # Utilities.tts_custom(say=f"{target_ip} is now online")


                    # SET ONLINE
                    online = True
                    delay = 10


                    if verbose:
                        console.print(f"[{c1}][+][/{c1}] Node Online: [{c3}]{target_ip} ")


                    
                    # UPDATE CLS STATUS
                    if first:
                        first = False
                    else:
                        cls.nodes_online += 1

                        # PUSH STATUS
                        Network_Scanner.node_changer(node_online=1)

                

                # ALREADY ONLINE
                elif response:



                    if verbose:
                        console.print(f"[{c1}][+][/{c1}] Still online: [{c3}]{target_ip}")

                


                # NO RESPONSE // NOW OFFLINE
                else:

                    if online == False:

                        # TALK
                        Utilities.tts_google(say=f"{target_ip} is now offline")



                        if verbose:
                            console.print(f"[{c1}][+][/{c1}] Node Offline: [{c3}]{target_ip} ")

                        

                        # UPDATE CLS STATUS
                        cls.nodes_offline += 1
                        cls.nodes_online -= 1

                        # PUSH STATUS
                        Network_Scanner.node_changer(node_offline=1, node_online=-1)



                        # APPEND DELAY // REDUCE NETWORK TRAFFIC
                        delay += 5 if delay < 20 else 0
                    
                    
                    # TRY ONE MORE PING BEFORE WE MAKE IT OFFLINE
                    else:

                        delay = 0
                        online = False
                


                # WAIT OUT THE DELAY
                time.sleep(delay)
            

            except Exception as e:
                console.print(f"Exception Error: ")
    
    
    
    @classmethod # THIS WILL NOT BE USED BEYOND TESTING // DONT TAKE SERIOUS 
    def node_changer(cls, node_online=0, node_offline=0):
        """This method will be responsible for updating node status to a json file"""
        

        # PULL JSON
        data = File_Handling.get_json(verbose=True)

        data["nodes_online"] += node_online
        data["nodes_offline"] += node_offline


        # PUSH JSON
        File_Handling.push_json(data=data, verbose=True)

    

    @classmethod
    def rate_limiter(cls, target_ip, verbose=0, timeout=60, count=100):
        """This method will be responsible for tracking/rate limiting a target"""


        # LET THE USER KNOW
        console.print(f"[bold red]Rate limiting[/bold red] --> {target_ip}", style="bold red")


        # INFINITE LOOP
        while cls.SNIFF:

            # START TIME START
            time_start = time.time()

            sniff(filter=f"ip and host {target_ip}", store=0, count=count, timeout=timeout)

            # GET END TIME
            time_total = time.time() - time_start

            if time_total > 60:


                # WARN USER OF RATE TRIGGER
                Utilities.flash_lights(action="alert", say=f"CODE RED,I Have found a rogue device with the ip of: {target_ip}. I will now begin to smack them off the internet!")

                # PRINT
                console.print("Succesfully warned the user")


    @classmethod
    def main(cls):
        """This will be responsible for performing class wide logic"""


        # SET VARS
        cls.SNIFF = True
        cls.scan_delay = 20
        cls.subnet_devices = []

        cls.nodes_online = 0
        cls.nodes_offline = 0




        # GET IFACE
        iface = Utilities.get_interface()
        
        time.sleep(1)

        # PERFORM ARP SCAN
        Network_Scanner.controller(iface=iface, target="192.168.1.0/24")




# STRICTLY FOR MODULE WIDE TESTING
if __name__ == "__main__":

    use = 1
    

    if use:
        Network_Scanner.main()