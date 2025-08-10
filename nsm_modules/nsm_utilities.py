# THIS MODULE WILL BE FOR UTILITIES



# UI IMPORTS
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()

# ETC IMPORTS
import sqlite3, os, requests, threading, time
from datetime import datetime

# VOICE 
from gtts import gTTS
import pyttsx3



# NSM IMPORTS
from nsm_files import File_Handling




class Utilities():
    """This will be responsible for common utilities"""

    # CLASS VAR
    talk = True


    def __init__(self):
        pass
    


    @classmethod
    def get_interface(cls):
        """This method will be used to get the user interface and automatically create a file saving it for default use"""

        
        try:
            # SET DEFAULT IFACE IF AVAILABLE
            data = File_Handling.get_json()
            def_iface = data['iface']


            # GIVE OPTION FOR DEFAULT
            if def_iface != "":
                use = f"or press enter for {def_iface}"
            
            else:
                use = ""

            
            while True:
                iface = console.input(f"[bold blue]Enter iface {use}: ").strip()
                

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
                    File_Handling.push_json(data=data)

                    return iface
            

        # ERROR 
        except Exception as e:
            console.print(f"[bold red]Exception Error:[yello] {e}")



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


    
    @staticmethod
    def tts_espeak(cls, say):
        """This method will be responsible for speaking aloud text"""


        say = str(say)

        os.system(f"espeak -p 20 {say}")
    


    @staticmethod
    def tts_google(say=False):
        """This will use a new approach to speaking"""


        try:
            tts = gTTS(say, tld='com.au')
            tts.save("output.mp3")
            os.system("mpg123 output.mp3")
        
        except Exception as e:
            console.print(f"[bold red]Exception Error:[bold yellow] {e}")
    


    @staticmethod
    def tts_custom(say):
        """This will use a apt install tool"""

        import os

        text = "ATTENTION. ATTENTION. ATTENTION. Theres has been a new device found on your network with the ip address of: 192.168.1.27. Now launching Reverse Attack"
        os.system(f'edge-tts --voice en-US-GuyNeural --rate="+10%" --text "{say}" --write-media jewl.mp3 && mpg123 jewl.mp3')

    
    @staticmethod
    def tts_def( letter, voice_rate= 20):
        """Responsible for text to speech"""

        engine = pyttsx3.init()
        
        voices = engine.getProperty('voices')
        rate = engine.getProperty('rate')

        # SET VOLUME
       # volume = engine.getProperty('volume')
        
       
        
        try:
           # engine.setProperty('volume', 20)
            engine.setProperty('rate', rate - voice_rate)
           
        except Exception as e:
            console.print(e)
  

        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
           # console.print("Voice set to 1")
        
        else:
            engine.setProperty('voice', voices[0].id)
           # console.print("voice set to 0")

        engine.say(letter)
        engine.runAndWait()



    @classmethod
    def flash_lights(cls, say=False, server_ip="192.168.1.51", action="alert", verbose=False):
        """This method will be responsible for flashing lights via web api to esp"""


        # TALK TO
        if say and cls.talk:

            # TURN IT OFF
            cls.talk = False

            # THREAD IT & CONTINUE
            threading.Thread(target=Utilities().tts_espeak, args=(say, ),daemon=True).start()
            time.sleep(2)

            # TURN BACK ON
            cls.talk = True
            
        

        # FORM URL
        url = f"http://{server_ip}/{action}"
        response = requests.post(url)

        if response.status_code == 200:

            if verbose:
                console.print("Succesfully flashed light", style="bold green")
        

        else:

            if verbose:
                console.print("Failed to flash lights", style="bold red")



# STRICTLY FOR MODULAR TESTING
if __name__ == "__main__":
    
   # Utilities().tts_def(letter="howdy. I am now ur slave")
    Utilities.flash_lights(say="CODE RED,I Have found a rogue device with the ip of: 192.168.1.1. I will now begin to smack them off the internet!")
   # Utilities.tts_custom(say="howdy, im ur slave")
  #  Utilities.tts_google(say=f"CODE RED,I Have found a rogue device with the ip of: 192.168.1.1. I will now begin to smack them off the internet!")


