# THIS MODULE WILL BE FOR UTILITIES



# UI IMPORTS
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()


# NETWORK IMPORTS
import socket, requests, manuf, ifcfg
from scapy.all import sniff, ARP, IP, ICMP, srp, Ether, conf, sr1
#import nmap



# ETC IMPORTS
import sqlite3, os, threading, time, random, json
from datetime import datetime, timedelta
import argparse, subprocess


# VOICE 
from gtts import gTTS
import pyttsx3
#from vonage import Auth, Vonage
#from vonage_voice import CreateCallRequest, Phone, ToPhone


# NSM IMPORTS
from nsm_files import File_Handling, Push_Network_Status



conf.use_pcap = True
LOCK = threading.Lock()



class Connection_Handler():
    """This module will house connection orientated methods"""


    # STORE LAN NODES DATA
    nodes = {}

    def __init__(self):
        pass


    
    @staticmethod
    def get_conn_status(verbose=True):
        """This method will be a blocking method for if the user is online or not"""


        # MULTIPLE OPTIONS IN CASE ONE IS DOWN OR CANT BE REACHED FOR CERTAIN REASONS
        domains = ["google.com", "cloudflare.com", "github.com", "wikipedia.org", ]


        try:

            host = socket.gethostbyname(random.choice(domains))

            if host:
                
                if verbose:
                    console.print(f"[bold blue]Connection Status:[bold green] ONLINE")
                
                return True
            
            
            console.print(f"[bold blue]Connection Status:[bold red] OFFLINE")
            return False
        


        except Exception as e:

            # OUTPUT
            if verbose:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")
                console.print(f"[bold blue]Connection Status:[bold red] OFFLINE")


            return False


    @staticmethod
    def establish_reconnection(verbose=False):
        """This method will be called upon if there is a connection interruption"""


        # CHECK DELAY
        delay = False


        while True:
            
            if delay:
                time.sleep(delay)

            try:

                status = Connection_Handler.get_conn_status(verbose=False)


                if status:

                    console.print(f"Connection Status back online  -  Resuming program!", style="bold green")

                    
                    # RESUME PROGRAM
                    return True
                

                else:
                    
                    if verbose:
                        console.print(f"Connection status still offline", style="bold red")

                    delay = 3
            

            except Exception as e:

                if verbose:
                    console.print(f"Connection status still offline  -  {e}", style="bold red")

                delay = 3

    
    @classmethod
    def status_checker(cls, target_ip, target_mac, host, vendor, iface):
        """This method will be responsible for monitroing the connection status of the target_ip"""


        
        # CURRENTLY TESTING
        #Utilities.announce_device(ip=target_ip, host=host, vendor=vendor, type=1)


        # LEGACY CONTROLLER
        leg = False


        # VARS
        verbose = False
        RESET = 0.5
        delay = 0.5
        timeout = 0.5
        online = 0
        count = 0
        
        # COUNT THE AMOUNT OF SCANS PERFORMED
        scans = 0


        # COLORS
        c1 = "bold red"
        c2 = "bold blue"
        c3 = "bold purple"
        c4 = "bold yellow"


        # GET LOCAL
        local_ip = File_Handling.get_json(verbose=False)["local_ip"]


        # PACKETS
        arp = Ether(dst=target_mac) / ARP(pdst=target_ip)
        ping = IP(dst=target_ip) / ICMP()


        # FOR LOCAL DEVICE // THIS WILL PREVENT ADAPTER FROM SENDING PACKETS TO ITSLEF RESULTING IN CONSTANT JUMPS BETWEEN ONLINE AND OFFLINE STATUS
        #local = File_Handling.get_json(verbose=False)["local_ip"]
  

        if target_ip == File_Handling.get_json(verbose=False)["local_ip"]:

            console.print("[bold green][+] [bold yellow]found local --> ", target_ip)


            # DOESNT WORK
            skip = True

            cls.nodes[target_ip] = {
                "target_ip": target_ip,
                "target_mac": target_mac,
                "host": host,
                "vendor": vendor,
                "status": "online"
            }




            if not skip:

                while True:

                    try:

                        # PING YOURSELF
                    # ping = IP(dst=target_ip) / ICMP()

                        #response = srp(arp, iface=iface, timeout=timeout, verbose=0)[0]
                        
                        # DOUBLE CHECK
                        #if response in [None, False]:
                        # response = sr1(ping, iface=iface, timeout=timeout, verbose=0)

                        if response:

                            cls.nodes[target_ip] = {
                            "target_ip": target_ip,
                            "target_mac": target_mac,
                            "host": host,
                            "vendor": vendor,
                            "status": "online"
                        }
                            

                            # RESET
                            count = 0
                            
                        elif count > 6:

                            cls.nodes[target_ip] = {
                            "target_ip": target_ip,
                            "target_mac": target_mac,
                            "host": host,
                            "vendor": vendor,
                            "status": "offline"
                        }
                            
                        elif count > 6:
                            count += 1
                            

                        # WAIT
                        time.sleep(10)
                    

                    except Exception as e:
                        console.print(f"[bold red]Exception Error:[bold yellow] {e}")
                    
                
            
            

        # SUBNET DEVICES // NOT HOST DEVICE
        else:

            while True:

                
                try:

                    # APPEND
                    count += 1

                    # GET
                    with LOCK:
                        response = srp(arp, iface=iface, timeout=timeout, verbose=0)[0]
                        
                        # DOUBLE CHECK
                        if not response:
                            pass
                           # console.print("2")
                            #response = sr1(ping, iface=iface, timeout=timeout, verbose=0)


                    # IF NOW ONLINE
                    if response and not online:
                        
                        # UPDATE
                        online = True
                        delay = RESET
                        timeout = RESET
                        count = 0


                        if verbose:
                            console.print(f"[{c1}][+][/{c1}] Node Online: [{c4}]{target_ip} ")


                        
                        # NEW WAY
                        cls.nodes[target_ip] = {
                            "target_ip": target_ip,
                            "target_mac": target_mac,
                            "host": host,
                            "vendor": vendor,
                            "status": "online"
                        }

                        # UPDATE STATUS
                        status = "online"

                        # ANNOUNCE
                        if scans > 3:
                            Utilities.announce_device(ip=target_ip, host=host, vendor=vendor, type=2, status=status)


                        # PUSH STATUS
                        if leg:
                            with LOCK:
                                Push_Network_Status.push_device_info(
                                    
                                    target_ip=target_ip,
                                    target_mac=target_mac,
                                    host=host,
                                    vendor=vendor,
                                    status="online"
                                    
                                    )
                        
                        
                        # DELAY
                        delay = RESET   
                        timeout = RESET
                        time.sleep(delay)
                    

                    # STILL ONLINE
                    elif response:

                        if verbose:
                            console.print(f"[{c1}][+][/{c1}] Node Online still: [{c4}]{target_ip} ")


                        # DELAY
                        time.sleep(delay)


                        # TRY AND RE QUERY VENDOR IF NONE
                        if not vendor:
                            vendor = Utilities.get_vendor(mac=target_mac)
                            cls.nodes[target_ip] = {
                                "target_ip": target_ip,
                                "target_mac": target_mac,
                                "host": host,
                                "vendor": vendor,
                                "status": "online"
                            }


                            #console.print("got --> ", vendor)
                        

                    

                    # NOW OFFLINE
                    elif count > 6:


                        # NEW WAY
                        cls.nodes[target_ip] = {
                            "target_ip": target_ip,
                            "target_mac": target_mac,
                            "host": host,
                            "vendor": vendor,
                            "status": "offline"
                        }
                        

                        # UPDATE STATUS
                        status = "offline"


                        #console.print(response)
                        


                        # ANNOUNCE
                        if online:
                            Utilities.announce_device(ip=target_ip, host=host, vendor=vendor, type=2, status=status)

                        # PUSH STATUS
                        if leg:
                            with LOCK:
                                Push_Network_Status.push_device_info(
                                    
                                    target_ip=target_ip,
                                    target_mac=target_mac,
                                    host=host,
                                    vendor=vendor,
                                    status="offline"
                                    
                                    )
                        

                        # OFFLINE
                        online = False
                        

                        # DELAY
                        delay = RESET   
                        timeout = RESET
                        time.sleep(delay)
                    

                    
                    # RE-TRY ARP
                    else:

                        count += 1
                        delay += 0.5
                        timeout += 0.5 if timeout < 2.5 else 2.5
                        delay += 0.5 if delay < 2.5 else 2.5
                    

                        time.sleep(delay)


                        if verbose:
                            console.print("arping -- ", target_ip)
                    

                    # FOR TESTING
                    if verbose:
                        console.print("here -- ", target_ip)
                    scans += 1
                

                except Exception as e:
                        console.print(e)


                        # REMOVE FROM LIST
                        from nsm_network_scanner import Network_Scanner
                        Network_Scanner.subnet_devices.remove(target_ip)


                        # NEW WAY
                        cls.nodes[target_ip] = {
                            "target_ip": target_ip,
                            "target_mac": target_mac,
                            "host": host,
                            "vendor": vendor,
                            "status": "offline"
                        }


                        # UPDATE STATUS
                        status = "offline"


                        # ANNOUNCE
                        Utilities.announce_device(ip=target_ip, host=host, vendor=vendor, type=2, status=status)


                        # SET OFFLINE (FOR NOW)
                        if leg:
                            with LOCK:
                                Push_Network_Status.push_device_info(
                                    
                                    target_ip=target_ip,
                                    target_mac=target_mac,
                                    host=host,
                                    vendor=vendor,
                                    status="offline"
                                    
                                    )


                        # KILL THREAD
                        console.print(f"[bold red][-] Thread Killed:[bold yellow] {target_ip}")

                        break

                
    @staticmethod
    def get_local_ip(iface=False, verbose=True):
        """This method will be responsible for getting local ip"""




        try:
            # SET DEFAULT IFACE IF AVAILABLE
            data = File_Handling.get_json(verbose=False)
            def_local_ip = data['local_ip']


            # GIVE OPTION FOR DEFAULT
            if def_local_ip != "":
                use = f"[bold yellow]or press enter for {def_local_ip}"
            
            else:
                use = ""

            
            
            local_ip = console.input(f"[bold green]Enter your local IP {use}: ").strip()
            

            # NEED SOME TYPE OF IFACE
            if local_ip == "" and def_local_ip == "":

                console.print("You must enter subnet to procced silly", style="bold red")
                exit()
            
            # ROLL BACK TO DEFAUT
            elif local_ip == "":
                local_ip = def_local_ip

                return local_ip
            

            
            # SET NEW DEF IFACE
            else:
                data['local_ip'] = local_ip
                
                # NOW TO UPDATE SETTINGS
                File_Handling.push_json(data=data, verbose=False)

                return local_ip
            

        # ERROR 
        except Exception as e:
            console.print(f"[bold red]Exception Error:[yello] {e}")

            # EXIT PROGRAM
            exit()
            
    

    @classmethod
    def daily_update(cls, time_start=False):
        """This method will be responsible for pushing daily updates to discord of network health"""


        # VARS
        a1 = ["21", "33", "19"]
        a2 = ["30", "0", "55"]
        
        
        # SET TIME
        if time_start:
            cls.time_start = time_start

            return

        
        # GET CURRENT TIME STAMP AND SEE IF IT MATCHES TRIGGER
        time_now = datetime.now().strftime("%H:%M")
        t1 = time_now.split(":")[0]
        t2 = time_now.split(":")[1]



        # MORNING UPDATE
        if t1 in a1 and t2 in a2:

            # PULL DATA
            data = Push_Network_Status.get_device_info(verbose=False)


            #console.print(data)

            
            # GET VARS
            nodes_online = data["summary"]["nodes_online"]
            nodes_total = data["summary"]["nodes_total"]
            nodes_offline = nodes_total - nodes_online
            time_elapsed = str(timedelta(seconds=time.time() - cls.time_start)).split('.')[0]

            notes = [
                "Rise with power,  Bari",
                "The network bows to you, Master  Bari",
                "Awaken — destiny calls,  Bari",
                "Good morning, Guardian of the Grid",
                "Another day, another conquest,  Bari",
                "System initialized —  Bari is online",
                "The empire awaits its commander,  Bari",
                "Grand awakening, Protector of Packets",
                "Good energy uploaded, Bari",
                "All systems stand ready for you,  Bari"
            ]

            notez = "Good Morning,   Grand Master Bari"


            # THE MORNING NTE
            LINE = "-" * 50
            LINEE = "-" * 25
            LINEEE = "-" * 34
            morning = notez #random.choice(notes)
            time_stamp = f"Timestamp: {datetime.now().strftime( "%m/%d/%Y - %H:%M:%S")}"
            summary = f"Online Devices: {nodes_online}\nOffline Devices: {nodes_offline}\nTotal Devices: {nodes_total}"
            program_elapsed_time = f"Total Program elapsed time: {time_elapsed}"


            updatee = (
                f"{LINE}\n"
                f"{time_stamp}\n"
                f"{LINE}\n\n"
                f"{morning}\n\n"
                f"{LINEE}\n"
                f"{summary}\n"
                f"{LINEE}\n\n"
                f"{program_elapsed_time}\n"
                f"{LINE}"
            )
            


            # CREATE UPDATE
            update = (
                    f"{LINE}\n"
                    f"{morning}\n\n"
                    f"{LINEEE}\n"
                    f"{time_stamp}\n"
                    f"{LINEEE}\n\n"
                    f"{LINEE}\n"
                    f"{summary}\n"
                    f"{LINEE}\n\n"
                    f"{program_elapsed_time}\n"
                    f"{LINE}"
                    )
            

            # PUSH UPDATE
            Utilities.push_to_discord(data=update)

            

        
            # ADD A WAITING PERIOD SO THIS TRIGGER CAN PAST // BLOCKING FOR NOW
            time.sleep(61)


class Utilities():
    """This will be responsible for common utilities"""

    # CLASS VAR
    talk = True
    free = True
    UI = False

    def __init__(self):
        pass


    @staticmethod
    def clear_screen():
        """This will be used for a smoother cleaner transition"""

        if os.name == "posix":

            os.system("clear")

        
        elif os.name == "nt":

            os.system("cls")


    @staticmethod
    def change_settings():


        parser = argparse.ArgumentParser(description="Settings menu")
        

        parser.add_argument(
            help="Add discord webhook",

            )
    

    @staticmethod
    def phone_call():
        """This method will be responsible for performing phone calls to the user"""


        # yDRQKlgA09zYE5bo  // https://dashboard.nexmo.com/make-a-voice-call



        # CALL
        phone_to = "813-446-0242"
        phone_from = ""




        try:


            # PRINT
            console.print("responseresponse")




        
        except Exception as e:
            console.print(f"[bold red]Phone call Exception Error:[bold yellow] {e}")


  
    @classmethod
    def announce_device(cls, ip, type, status=False, vendor=False, host=False, verbose=False):
        """This method will announce devices based on host or ip"""



        with LOCK:


            # QUEUE SERVICE
            while not cls.free:
                pass

            
            # PAUSE OTHER THREADS
            cls.free = False


            # FOR NEW DEVICES FOUND ON THE NETWORK
            if type in [1, "new"]:


                if host:

                    note = f"Attention, there was a new device detected with the name of: {host}"
                

                elif vendor:

                    note = f"Attention, there was a new device detected with the vendor of: {vendor}" 

                
                else:

                    note = f"Attention, there was a new device detected with the IP Address of: {ip}"
            
            

            # FOR STATUS UPDATE ON DEVICE  (ONLINE/OFFLINE)
            elif type in [2, "status"]:


                if host:
                    
                    note = f"{host} is now {status}"


                elif vendor:

                    note = f"{vendor} is now {status}" 
                

                else:

                    note = f"{ip} is now {status}"

            

            # VERBOSE
            if verbose:
                console.print(f"{note}")
            
            # NOW ANNOUNCE
            TTS.tts_google(say=note)
            #TTS.tts_def(letter=note, voice_rate=5)


            # UNPAUSE
            cls.free = True


    @staticmethod
    def push_to_discord(data, verbose=True):
        """This method will be used to push (post)data info to discord"""


        # VARS
        count = 3
        timeout = 3

        
        # GET API KEY
        api_key = File_Handling.get_json(type=2, verbose=False)['api_key_discord']


        # FORM DATA
        headers = {"content-type": "application/json"}
        payload = {"content": data}


        while count > 0:

            try:

                response = requests.post(api_key, data=json.dumps(payload), headers=headers, timeout=timeout)


                if response.status_code in [200, 204]:

                    if verbose:

                        console.print("[bold green][+] Discord push Successfull")

                    
                    break
                

                else:


                    if verbose:
                        
                        console.print("[bold red][+] Discord push Failed")


                    count =- 1
                    timeout += 1
            


            except Exception as e:

                if verbose:
                    console.print(f"[bold red]Discord nsm_modules/output.mp3Exception Error:[bold yellow] {e}")
                
                count =- 1
                timeout += 1


    @staticmethod
    def get_time_stamp(ui):
        """This lets you know the terminal is started"""

        time_stamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
        console.print(f"\n{ui.upper()} Mode Activated  -  Timestamp: {time_stamp}", style="bold green")



    @staticmethod
    def get_subnet():
        """This method will be responsible for getting a valid subnet"""



        try:
            # SET DEFAULT IFACE IF AVAILABLE
            data = File_Handling.get_json(verbose=False)
            def_subnet = data['subnet']


            # GIVE OPTION FOR DEFAULT
            if def_subnet != "":
                use = f"[bold yellow]or press enter for {def_subnet}"
            
            else:
                use = ""

            
            
            subnet = console.input(f"[bold green]Enter subnet {use}: ").strip()
            

            # NEED SOME TYPE OF IFACE
            if subnet == "" and def_subnet == "":

                console.print("You must enter subnet to procced silly", style="bold red")

            
            # ROLL BACK TO DEFAUT
            elif subnet == "":
                subnet = def_subnet

                return subnet
            

            
            # SET NEW DEF IFACE
            else:
                data['subnet'] = subnet
                
                # NOW TO UPDATE SETTINGS
                File_Handling.push_json(data=data, verbose=False)

                return subnet
            

        # ERROR 
        except Exception as e:
            console.print(f"[bold red]Exception Error:[yello] {e}")


    @classmethod
    def gui_or_cli(cls):
        """This method will be responsible for the user choosing between cli or gui"""


        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"


        try:
            
            # GET INPUT
            choice = console.input(f"[{c4}]Do you want to load[/{c4}] [{c2}]CLI or GUI?: ").strip().lower()


            if choice in ["cli", "1", ""]:

                return "cli"
            
            elif choice in ["gui", "2"]:

                return "gui"
            

            # NOT VALID
            console.print(f"False value given", style="bold red")

            # EXIT
            exit()

        

        except Exception as e:
            console.print(f"[bold red]Exception Error:[bold yellow] {e}")


            # EXIT
            exit()


    @staticmethod
    def get_valid_interface():
        """This will be responsible for making sure the iface given works before procceding with further logic"""

        
        # LOOP 4 ERRORS
        while True:


            try:


                # GET IFACE
                iface = Utilities.get_interface()


                # NOW TRY IT
                sniff(iface=iface, timeout=0.1)


                # RETURN VALID IFACE
                return iface
            

            except Exception as e:
                console.print(e, "\n")

                
                # EXIT PROGRAM
                exit()


    @classmethod
    def get_interface(cls):
        """This method will be used to get the user interface and automatically create a file saving it for default use"""

        
        try:
            # SET DEFAULT IFACE IF AVAILABLE
            data = File_Handling.get_json(verbose=False)
            def_iface = data['iface']


            # GIVE OPTION FOR DEFAULT
            if def_iface != "":
                use = f"[bold yellow]or press enter for {def_iface}"
            
            else:
                use = ""

            
           
            iface = console.input(f"[bold green]Enter iface {use}: ").strip()
            

            # NEED SOME TYPE OF IFACE
            if iface == "" and def_iface == "":

                console.print("You must enter iface to procced silly", style="bold red")

            
            # ROLL BACK TO DEFAUT
            elif iface == "":
                iface = def_iface

                return iface
            

            
            # SET NEW DEF IFACE
            else:
                data['iface'] = iface
                
                # NOW TO UPDATE SETTINGS
                File_Handling.push_json(data=data, verbose=False)

                return iface
        

        # ERROR 
        except Exception as e:
            console.print(f"[bold red]Exception Error:[yello] {e}")
    

    @staticmethod
    def get_host(target_ip, verbose=False):
        """This method will be responsible for getting the target host"""
        
        try:
            
            # GET HOST
            host = socket.gethostbyaddr(target_ip)[0]


            if host.split('.')[0]:

                host = host.split('.')[0]
                

            #console.print(host)
            #console.print(host.split(','))


            # RETURN VALUE
            return host
        

        except Exception as e:

            if verbose:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")

    
    @staticmethod
    def get_vendor(mac:str):
        """This class will be responsible for getting the vendor"""
  
        
        # FOR DEBUGIGNG
        verbose = False


        # TRY API FIRST
        url = f"https://api.macvendors.com/{mac}"


        try:
            response = requests.get(url=url, timeout=3)

            if response.status_code in {200, 204}:

                if verbose:
                    console.print(f"Successfully retrieved API Key: {response.text}")

                
                return response.text if response.text != None else manuf.MacParser("manuf.txt").get_manuf_long(mac=mac)
            
            else:
                
                if verbose:
                    console.print(response.text)
                
                response = manuf.MacParser("manuf.txt").get_manuf_long(mac=mac)
                return response

        
        
        # DESTROY ERRORS
        except Exception as e:

            if verbose:
                console.print(f"[bold red]Exception Error:[yellow] {e}")

            
            
            #response = vendors.lookup(mac=mac) if vendors.lookup(mac=mac) else None

            response = manuf.MacParser("manuf.txt").get_manuf_long(mac=mac)
 
 
    @classmethod
    def get_os(cls, target_ip, verbose=1):

        nm = nmap.PortScanner()

        results = nm.scan(hosts=target_ip, arguments="-O")


        # VERBOSE TESTING
        if verbose:

            console.print(f"OS DETECTION: {results}")

        

    @classmethod
    def flash_lights(cls, CONSOLE, say=False, server_ip="192.168.1.51", action="alert", verbose=False):
        """This method will be responsible for flashing lights via web api to esp"""


        # TALK TO
        with LOCK:
            if say and cls.talk:

                # TURN IT OFF
                cls.talk = False

                # THREAD IT & CONTINUE
                #threading.Thread(target=Utilities().tts_espeak, args=(say, ),daemon=True).start()
                #time.sleep(2)

                # TURN BACK ON
                cls.talk = True
            
        

        # FORM URL
        try:

            url = f"http://{server_ip}/{action}"
            response = requests.post(url)

            if response.status_code == 200:

                if verbose:
                    CONSOLE.print("Succesfully flashed light", style="bold green")
            

            else:

                if verbose:
                    CONSOLE.print("Failed to flash lights", style="bold red")
        

        except Exception as e:

            if verbose:
                CONSOLE.print(f"[bold red]Exception Error:[bold yellow] {e}")


    @classmethod
    def push_sql_db(cls, proto, ip_src, ip_dst, port_src, port_dst, pkt_ttl, pkt_len, verbose=True, traffic_type=2):
        """This method will be used to push and pull info from the SQL DB"""


        # GET SQL PATH
        sql = File_Handling.path_for_sql(get=True)


        # CREATE DB PATH 
        path = sql / "network_traffic_all.db"


        # PATH 
        if traffic_type == 1:
            db = "network_traffic_all.db"

        elif traffic_type == 2:
            db = "network_traffic_anamolies.db"



        # GET TIMESTAMP
        time_stamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")




        # CREATE DATABASE CONNECTION
        with sqlite3.connect(f"{db}") as conn:


            # TURN ON AUTO-COMMIT
            conn.autocommit = True


            # MAKE CURSOR
            cursor = conn.cursor()


            # MAKE SURE TABLE IS CREATED
            cursor.execute("""CREATE TABLE IF NOT EXISTS network_traffic (
                           
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           time_stamp TEXT,
                           proto TEXT,
                           ip_src TEXT,
                           ip_dst TEXT,
                           port_src INTEGER,
                           port_dst INTEGER,
                           ttl INTEGER,
                           pkt_len INTEGER

                           )""")
            

            # NOW TO ENTER VALUES
            cursor.execute("""INSERT INTO network_traffic (time_stamp, proto, ip_src, ip_dst, port_src, port_dst, ttl, pkt_len) 
                           
                           VALUES (?,?,?,?,?,?,?,?)""",  # 8 VALUES
 

                           # INSERT VALUES
                           (time_stamp, proto, ip_src, ip_dst, port_src, port_dst, pkt_ttl, pkt_len)
                           
                           
                           )
           
            
            # SAVE CHANGES
            conn.commit()


            # IF VERBOSE
            if verbose:
                console.print(f"Successufully commited changes to SQL DB", style="bold green")



# GAVE TTS METHODS ITS OWN CLASS FOR CLEANER STORING
class TTS():
    """This class will be responsible for holding all TTS variations"""


    # WILL USE THIS VARIABLE FOR DRIVER ERROR/MISCONFIG
    drive_error = False


    @staticmethod
    def tts_espeak( say):
        """This method will be responsible for speaking aloud text"""


        say = str(say)

        os.system(f"espeak  {say}")
    


    @classmethod
    def tts_google(cls, say=False):
        """This will use a new approach to speaking"""

        

        # TO PREVENT DRIVER ERRORS
        if not cls.drive_error: 


            try:

                tts = gTTS(say)
                tts.save("output.mp3")

                subprocess.run(
                    ["mpg123", "output.mp3"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                #os.system("aplay output.mp3 2>/dev/null")


                #console.print("i was able to print")
                #time.sleep(3)
            
            except Exception as e:
                console.print(f"[bold red]TTS Driver - Exception Error:[bold yellow] {e}")


                # DRIVER ERROR
                cls.drive_error = True    


    @staticmethod
    def tts_custom(say):
        """This will use a apt install tool"""

        import os

        text = "ATTENTION. ATTENTION. ATTENTION. Theres has been a new device found on your network with the ip address of: 192.168.1.27. Now launching Reverse Attack"
        os.system(f'edge-tts --voice en-US-GuyNeural --rate="+10%" --text "{say}" --write-media jewl.mp3 && mpg123 jewl.mp3')

    
    @classmethod
    def tts_def(cls, letter, voice_rate= 20):
        """Responsible for text to speech"""


        # IF DRIVER ALREADY THREW A ERROR
        if not cls.drive_error:

            engine = pyttsx3.init()
            
            voices = engine.getProperty('voices')
            rate = engine.getProperty('rate')


            # SET VOLUME
        # volume = engine.getProperty('volume')


            #console.print(f"{letter}")

            if letter == "start":
                console.print("Initializing...", style="bold yellow")
                letter = "Initializing"
            
        
            
            try:
            # engine.setProperty('volume', 20)
                engine.setProperty('rate', rate - voice_rate)
            

                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                # console.print("Voice set to 1")
                
                else:
                    engine.setProperty('voice', voices[0].id)
                # console.print("voice set to 0")
                

                    # WAIT IN QUEUE
                    while not engine.isBusy():
                        pass

                    # NOW SPEAK
                    engine.say(letter)
                    engine.runAndWait()
                    engine.stop()
                

            except Exception as e:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")


                # SET IT FALSE
                cls.drive_error = True
            





# STRICTLY FOR MODULAR TESTING
if __name__ == "__main__":
    

    # SET
    use = 4


    if use == 4:
        TTS.tts_google(say="yes sir, i will no begin to get to work.")



    if use == 3:

        h = "ATTENTION, new device detected on your network"

        TTS.tts_def(letter=h, voice_rate=10)
    
    if use == 1:
        mac = ""
     
        Connection_Handler.daily_update(time_start=time.time())


        time.sleep(2)

        while True:
            Connection_Handler.daily_update()


    elif use == 2:
        console.print("running")
        Utilities.flash_lights(say="CODE RED,I Have found a rogue device with the ip of: 192.168.1.1. I will now begin to smack them off the internet!")



