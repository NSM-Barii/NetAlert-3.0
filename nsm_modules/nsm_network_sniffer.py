# THIS PROJECT WILL BE ALPHA #1 FOR CREATING OUR FIRST MODEL // FOR UNKOWN 



# UI IMPORTS
import pyfiglet
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()


# NETWORK IMPORTS
from scapy.all import sniff, IP, TCP, UDP, ICMP
import socket, requests


# ETC IMPORTS
from concurrent.futures import ThreadPoolExecutor
import threading, time
from datetime import datetime


# ML --> IMPORTS
import pandas as pd, numpy, sqlite3


# NSM IMPORTS
from nsm_utilities import Utilities


# PREVENT RACE CONIDTIONS
LOCK = threading.Lock() 





class LLM():
    """This class will be responsible for controlling LLM"""


    def print():


        # START
        console.print(f"[bold green][+][bold yellow] LLM Background thread started")
        

        # INITAL TIME
        time_current = time.time()
        


        # LOOP INDEFINETLY
        while True:

            try:
            

                # TIME // PKTS
                pkts = Network_Sniffer.packet_queue
                

                # CPU LIMITER
                if len(pkts) > 10 or time_current > 1:


                    # COLOTS
                    c1 = "bold red"
                    c2 = "bold green"
                    c3 = "bold blue"


                    # NOW TO CALL LLM
                    for pkt in pkts:

                        if pkt:
                            
                            ip_src = pkt["ip_src"]
                            ip_dst = pkt["ip_dst"]
                            port_src = pkt["port_src"]
                            port_dst = pkt["port_dst"]
                            pkt_len = pkt["pkt_len"]
                            pkt_ttl = pkt["pkt_ttl"]
                            proto = pkt["proto"]

                            data = (f"{ip_src}:{port_src} -> {ip_dst}:{port_dst} - [{c1}]len:[/{c1}]{pkt_len} - [{c1}]ttl:[/{c1}]{pkt_ttl}")


                            console.print(f"[bold yellow][+][/bold yellow] {data}")
            

                    # CLEANSE QUE
                    with LOCK:
                        Network_Sniffer.packet_queue = []
                    time_current = time.time()
            
                
                # CPU BOUND
                else:
                    time.sleep(0.0001)
        
        
            except Exception as e:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")



class Network_Sniffer():
    """This class will be responsible for sniffing LAN wide traffic to then pass to a model"""


    def __init__(self):
        pass


    
    @classmethod
    def packet_sniffer(cls, iface="wlan0", filter="", test=False):
        """This will actual sniff the network"""


        # UPDATE RENDERABLE
        def update(panel):
            """This will be used to update panel renderable"""


            console.print("Background thread started", style="bold green")


            # COLORS
            c1 = "bold green"
            c2 = "bold red"
            c3 = "bold purple"

            
            # LOOP
            while True:


                # UPDATE VALUE
                panel.renderable = (f"[{c2}]Total Sniffed:[/{c2}] {cls.total_packets}  -  [{c2}]Total Nodes:[/{c2}] {len(cls.ips_found)}  -  [{c1}]NetAlert-3.0 Developed by NSM Barii")


                # DELAY
                time.sleep(1)




        # CREATE PANEL
        panel = Panel(
            renderable="Total Sniffed: 0  -  Total Nodes: 0  -  NetAlert-3.0 by Developed NSM Barii", 
            border_style="bold red",
            style="bold yellow",
            title="AI Powered IPS",
            expand=False
            )


        try: 
            
            # SINGLE MODULE TEST
            if test:

                # UPDATE PANEL LIVE
                with Live(panel, console=console, refresh_per_second=4):


                    # START BACKGROUND THREAD
                    
                    threading.Thread(target=update, args=(panel, ), daemon=True).start()
                

                    # SNIFF TRAFFIC
                    sniff(iface=iface, prn=Network_Sniffer.packet_parser, filter=filter, store=0)
            
            
            # CALLED UPON
            else:

                # SNIFF TRAFFIC
                sniff(iface=iface, prn=Network_Sniffer.packet_parser, filter=filter, store=0)
        

        
        # DESTROY ERRORS
        except Exception as e:
            cls.CONSOLE.print(f"\n[bold red]Exception Error:[bold yellow] {e}")
    

    @classmethod
    def packet_parser(cls, pkt):
        """This method will be responsible for parsing packet data"""


        def parser(pkt):
            """use this to pass the parser off to a seperate thread for crashing issues"""


            # LEGACY CONTROLLER
            leg = False 

            
            # CHECK FOR IP LAYER
            if pkt.haslayer(IP):
                

                # IP DST AND SRC
                ip_src = pkt[IP].src
                ip_dst = pkt[IP].dst

                # PROTOCOL // TCP OR UDP // FUCKING SKID
                proto = pkt.proto


                # PKT LENGTH AND TTL // SEE IF ITS UNUSUAL
                pkt_ttl = pkt.ttl
                pkt_len = len(pkt)


                # UDP PORTS
                if pkt.haslayer(UDP):

                    port_src = pkt[UDP].sport
                    port_dst = pkt[UDP].dport

                
                # TCP PORTS
                elif pkt.haslayer(TCP):

                    port_src = pkt[TCP].sport
                    port_dst = pkt[TCP].dport


                # ICMP PORTS
                elif pkt.haslayer(ICMP):

                    port_src = pkt[ICMP].type
                    port_dst = pkt[ICMP].code  

                
                # NOTHING ELSE
                else:

                    port_src = 0
                    port_dst = 0

                    # NOTIFY USER
                    cls.CONSOLE.print(f"else triggered", style="bold red")
                


                # MATCH INT TO PROTO
                proto = "UDP" if proto == 17 else "TCP" if proto == 6 else "ICMP" if proto == 1 else "IGMP" if proto == 2 else proto

                


                # PREVENT RACE CONDITIONS
                with LOCK:

                    # SMALL DELAY FOR SQL
                    #time.sleep(0.5)


                    # APPEND TOTAL
                    cls.total_packets += 1


                    # APPEND NEW IPS
                    if ip_src not in cls.ips_found:
                        cls.ips_found.append(ip_src)
                    
                    if ip_dst not in cls.ips_found:
                        cls.ips_found.append(ip_dst)


                    # PUSH TO SQL
                    if leg:
                        Network_Sniffer.packet_pusher(proto=proto, 
                                                ip_src=ip_src, ip_dst=ip_dst,
                                                port_src=port_src, port_dst=port_dst,
                                                pkt_ttl=pkt_ttl, pkt_len=pkt_len
                                                )
                    
                    
                    # ADD TO QUE FOR PACKET INSPECTION
                    else:
                        
                        # PACKAGE DATA
                        data = {
                            "ip_src": ip_src,
                            "ip_dst": ip_dst,
                            "port_src": port_src,
                            "port_dst": port_dst,
                            "proto": proto,
                            "pkt_len": pkt_len,
                            "pkt_ttl": pkt_ttl
                        }


                        cls.packet_queue.append(data)


        
        # THREAD IT
        threading.Thread(target=parser, args=(pkt,), daemon=True).start()



    @classmethod
    def packet_pusher(cls, proto, ip_src, ip_dst, port_src, port_dst, pkt_ttl, pkt_len):
        """This method will be responsible for pushing pkt parsed info to model and checking if it is normal or NOT"""

        
        # IF VERBOSE
        if cls.verbose:
            cls.CONSOLE.print(f"[bold red][+][/bold red] {proto} - {ip_src}:{port_src} --> {ip_dst}:{port_dst}  -  TTL: {pkt_ttl}  Len: {pkt_len}")
        


        # DELAY
        time.sleep(0.1)
        
        # PUSH INFO TO SQL DB
        Utilities.push_sql_db(proto=proto, 
                              ip_src=ip_src, ip_dst=ip_dst, 
                              port_src=port_src, port_dst=port_dst,
                              pkt_ttl=pkt_ttl, pkt_len=pkt_len,
                              verbose=False
                              )
        
    

    @classmethod
    def main(cls, iface=False,CONSOLE=console, get=False):
        """Class wide logic will be init from here"""

        
        # FOR DEBUGGING
        cls.verbose = True
        cls.CONSOLE = CONSOLE


        # PACKET INSPECTION QUE // FOR LLM
        cls.packet_queue = []


        # INIT CLASS VARS
        cls.network_traffic_normal = []
        cls.network_traffic_anamoly = []
        cls.ips_found = []
        cls.total_packets = 0 


        # GET IFACE
        if get:
            iface = Utilities.get_interface()


        # START LLM
        threading.Thread(target=LLM.print, args=(), daemon=True).start()


        # START SNIFFING
        Network_Sniffer.packet_sniffer(iface=iface)
    


if __name__ == "__main__":

    Network_Sniffer.main(get=True)
    