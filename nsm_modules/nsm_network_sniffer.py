# THIS PROJECT WILL BE ALPHA #1 FOR CREATING OUR FIRST MODEL // FOR UNKOWN 



# UI IMPORTS
import pyfiglet
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()


# NETWORK IMPORTS
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, DNS, BOOTP, SNMP
import socket, requests


# ETC IMPORTS
from concurrent.futures import ThreadPoolExecutor
import threading, time
from datetime import datetime


# ML --> IMPORTS
#import pandas as pd, numpy, sqlite3


# LLM --> IMPORTS
#from transformers import AutoTokenizer, pipeline
#from optimum.onnxruntime import ORTModelForSeq2SeqLM
#from transformers import AutoTokenizer
#from optimum.onnxruntime import ORTModelForSeq2SeqLM, pipeline


# NSM IMPORTS
from nsm_modules.nsm_utilities import Utilities


# PREVENT RACE CONIDTIONS
LOCK = threading.Lock() 





class LLM():
    """This class will be responsible for controlling LLM"""



    # LLM --> IMPORTS
    from transformers import AutoTokenizer, pipeline
    from optimum.onnxruntime import ORTModelForSeq2SeqLM


    """

    1,000 packets	~100 KB	✅
    10,000	~1 MB	✅
    100,000	~10 MB	✅
    1,000,000	~100 MB	✅ (with chunking)

    """
    
    @classmethod
    def llm_summarizer(cls, batch=False, full=False, verbose=True):
        """This module will be responsible for init and controlling the LLM"""



        # DEFAULT TASK
        if batch:
            prompt = "summarize: review this network traffic batch and briefly describe the main patterns, active protocols, and any unusual or suspicious activity."
        
        else:
            prompt = "summarize: based on all previous batch summaries, describe the overall network behavior, highlight recurring anomalies or device patterns, and point out any unusual or potentially malicious trends."
        

        query = f"{prompt}: {batch}" if batch else f"{prompt}: {full}"


        
        # THIS IS THE PRETRAINED MODEL THAT YOU DOWNLOADED
        LLM_NAME = "Xenova/t5-small"

        

        try:

            # INIT TOKENIZER
            tokenizer = AutoTokenizer.from_pretrained(LLM_NAME)

            # INIT MODEL
            model = ORTModelForSeq2SeqLM.from_pretrained(LLM_NAME)

            
            # CREATE SUMMARIZER
            summarizer = pipeline(task="summarization", model=model, tokenizer=tokenizer)

            # QUERY // GET RESPONSE
            response = summarizer(query)
            


            # VERBOSE
            if verbose:
                console.print(response)
            

            return response if response else "Failed"
    
        

        except Exception as e:
            console.print(f"[bold red]Exception Error:[bold yellow] {e}")
        

                

        return "Failed"




    @classmethod
    def print(cls, verbose=False):


        # START
        console.print(f"[bold green][+][bold yellow] LLM Background thread started")


        # COLOTS
        c1 = "bold red"
        c2 = "bold green"
        c3 = "bold blue"


        

        # INIT
        pkts = []
        summary_batch = []
        panel = Panel(renderable=f"[{c1}]pkts:[{c2}] {len(pkts)} - [{c1}]batch amount:[{c2}] {len(summary_batch)}")





        # INITAL TIME
        time_elapsed = time.time() 
        time_current = time.time()
        time.sleep(1)

        time_current = time.time() - time_current
        time_current = float((f"{time_current:.1f}"))
        summaries = []
        


        # LOOP INDEFINETLY
        with Live(panel, console=console, refresh_per_second=1):
                
            while True:

                try:
                

                    #  PKTS // PKT_FULL
                    pkts = Network_Sniffer.packet_queue


                    # FOR VERBOSE // DEBUGGING
                    if verbose:
                        console.print("testinggggggggggg")



                        # NOW TO CALL LLM
                        for pkt in pkts:

                            if pkt:


                                # EXTRACT META-DATA
                                ip_src = pkt["ip_src"]
                                ip_dst = pkt["ip_dst"]
                                port_src = pkt["port_src"]
                                port_dst = pkt["port_dst"]
                                pkt_len = pkt["pkt_len"]
                                pkt_ttl = pkt["pkt_ttl"]
                                proto = pkt["proto"]
                            

                                # FORM PKT LINE
                                data = (f"{proto} - {ip_src}:{port_src} -> {ip_dst}:{port_dst} - [{c1}]len:[/{c1}]{pkt_len} - [{c1}]ttl:[/{c1}]{pkt_ttl}")


                                
                                # OUTPUT
                                if verbose:
                                    console.print(f"[bold yellow][+][/bold yellow] {data}")

                            
                                # UPDATE PANEL
                                time_elapsed = time.time() - time_elapsed
                                panel.renderable = (f"[{c1}]Pkts:[{c2}] {len(pkts)} - [{c1}]Batch amount:[{c2}] {len(summaries)} - [{c1}]Elapsed Time:[{c2}] {time_elapsed:.1f}  -  [{c1}]Developed by NSM Barii")


                        # CLEANSE QUE
                        with LOCK:
                            #Network_Sniffer.packet_queue = []
                            time_current = time.time()

                    

                    
                    # SUMMARIZE LAST 1K PACKETS // WITH LLM
                    if len(pkts) > 1000:
                        console.print(len(pkts))


                        # GET SUMMARY
                        summary_batch = LLM.llm_summarizer(batch=pkts, verbose=True)


                        # APPEND THE SUMMARY AND TRACK
                        summaries.append(summary_batch)
                        with LOCK:
                            pkts = []

                        

                        # GET BATCH SUMMARY
                        if len(summaries) >= 100:
    

                            # GET FULL  
                            summary_full = LLM.llm_summarizer(full=True,  verbose=True)

                            
                            # CLEAN VARS 
                            summaries = [] 

                            
                            # VERBOSE
                            #if verbose:
                            console.print(f"[bold green]LLM Response:[/bold green] {summary_full}")

                            


                    # CPU DELAY
                    time.sleep(1)  

                    # UPDATE PANEL
                    time_elapsed = time.time() - time_elapsed
                    panel.renderable = (f"[{c1}]Pkts:[{c2}] {len(pkts)} - [{c1}]Batch amount:[{c2}] {len(summaries)} - [{c1}]Elapsed Time:[{c2}] {time_elapsed:.1f}  -  [{c1}]Developed by NSM Barii")

            
            
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


            try:
            
                # CHECK FOR IP LAYER
                if pkt.haslayer(IP):



                    # IP DST AND SRC
                    ip_src = pkt[IP].src if pkt[IP].src else "unkown"
                    ip_dst = pkt[IP].dst if pkt[IP].dst else "unkown"



                    # PROTOCOL // TCP OR UDP // FUCKING SKID
                    proto = pkt.proto


                    # PKT LENGTH AND TTL // SEE IF ITS UNUSUAL
                    pkt_ttl = pkt.ttl
                    pkt_len = len(pkt)


                    # UDP PORTS
                    if pkt.haslayer(UDP):

                        port_src = pkt[UDP].sport
                        port_dst = pkt[UDP].dport
                        proto = "UDP"

                    
                    # TCP PORTS
                    elif pkt.haslayer(TCP):

                        port_src = pkt[TCP].sport
                        port_dst = pkt[TCP].dport
                        proto = "TCP"


                    # ICMP PORTS
                    elif pkt.haslayer(ICMP):

                        port_src = pkt[ICMP].type
                        port_dst = pkt[ICMP].code  
                        proto = "ICMP"
                    

                    # ARP PORTS
                    elif pkt.haslayer(ARP):

                        port_src = pkt[ARP].psrc
                        port_dst = pkt[ARP].pdst
                        proto = "ARP"

                    
                    # DNS PORTS
                    elif pkt.haslayer(DNS):
                        port_src = pkt[DNS].sport
                        port_dst = pkt[DNS].dport
                        proto = "DNS"

                    
                    # DHCP PORTS
                    elif pkt.haslayer(BOOTP):
                        port_src = pkt[UDP].sport
                        port_dst = pkt[UDP].dport
                        proto = "DHCP"

                    
                    # SNMP PORTS
                    elif pkt.haslayer(SNMP):
                        port_src = pkt[SNMP].sport
                        port_dst = pkt[SNMP].dport
                        proto = "SNMP"

                    
                    # NOTHING ELSE
                    else:

                        port_src = 0    
                        port_dst = 0

                        # NOTIFY USER
                        cls.CONSOLE.print(f"else triggered", style="bold red")
                    




            except Exception as e:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")
                ip_src = "UNKOWN"
                ip_dst = "UNKOWN"
                proto = "UNKOWN"
            


            if pkt.haslayer(IP):
            

                # PROTOS
                protos = ["TCP", "UDP", "ARP", "ICMP", "DNS", "DHCP", "SNMP"]
                proto = proto if proto in protos else "UNKOWN"
                


                # MATCH INT TO PROTO // DEAPPRECIATED FEATURE
                if leg:
                    proto = "UDP" if proto == 17 else "TCP" if proto == 6 else "ICMP" if proto == 1 else "IGMP" if proto == 2 else proto


                protocols = {

                }

                    


                # PREVENT RACE CONDITIONS
                with LOCK:
                    

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


    

    # THIS METHOD WILL SOON BE DEAPPRECIATED
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


    go = 2
    
    if go == 2:

        from optimum.onnxruntime import ORTModelForSeq2SeqLM
        from transformers import AutoTokenizer
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

        # Load ONNX model + tokenizer
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        model = ORTModelForSeq2SeqLM.from_pretrained("google/flan-t5-base", export=True)

        # Clean input as a list of lines (not a tuple object)
        lines = [
            "- TCP - 192.168.1.2:44321 --> 8.8.8.8:443 - TTL: 64  Len: 150",
            "- TCP - 192.168.1.2:44322 --> 8.8.8.8:443 - TTL: 64  Len: 160",
            "- UDP - 192.168.1.5:49812 --> 1.1.1.1:53 - TTL: 128  Len: 90",
            "- UDP - 192.168.1.5:49813 --> 1.1.1.1:53 - TTL: 128  Len: 94",
            "- ICMP - 192.168.1.7 --> 192.168.1.1 - TTL: 64  Len: 98"
        ]

        # Format prompt correctly
        prompt = "summarize this network log in 3 bullet points:\n" + "\n".join(lines)

        # Tokenize and generate
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = model.generate(**inputs, max_length=200)

        # Show result
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("LLM Output:\n", summary)



    else:
        Network_Sniffer.main(get=True)
    2