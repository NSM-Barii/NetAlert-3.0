# THIS MODULE WILL BE FOR FILE HANDLING




# UI IMPORTS
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.console import Console
console = Console()
import http.client

# ETC IMPORTS
import os, time, threading
from datetime import datetime


# FILE IMPORTS
from pathlib import Path
import json




# SAFE FILE HANLDING
LOCK = threading.Lock()


# USE THIS TO FIX PREMISSION ERRORS
# sudo chown -R "$USER:$USER" ../../.data/netalert3/nodes.json


class File_Handling():
    """This method will be responsible for file creation and handling"""


    def __init__(self):
        pass


    @classmethod
    def create_base_dir(cls, verbose=False, get=False):
        """This single method will be responsible soley for creating def path"""

        
        # TRY
        try:
            USER_HOME = Path(os.getenv("SUDO_USER") and f"/home/{os.getenv('SUDO_USER')}") or Path.home()
            cls.base_dir = USER_HOME / "Documents" / "nsm_tools" / ".data" / "netalert3"
        except Exception as e:

            if verbose:
                console.print(e)
            
            # SWITCH BACK TO PATH
            cls.base_dir= Path.home() / "Documents" / "nsm_tools" / ".data" / "netalert3"
        

        # MAKE IT
        cls.base_dir.mkdir(parents=True, exist_ok=True)
            
        # RETURN FOR DIFERENT MODULES
        if get:
            #console.print("returning", style="bold red")
            
            return cls.base_dir
           

    @classmethod
    def path_for_sql(cls, get=False):
        """This will be responsible for creating and handling file path for db """

        
        # RETRIEVE AND RETURN SQL PATH
        if get:
            try:


                # CREATE BASE IN CASE
                File_Handling.create_base_dir()


                # MAKE SURE PATH IS SET            
                if cls.base_dir.exists():

                    path = cls.base_dir / "sql"

                    return path
                

            except Exception as e:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")


    @classmethod
    def get_json(cls, type="settings", verbose=True):
        """This will pull and return json info"""


        # MAKE SURE BASE IS VALID
        File_Handling.create_base_dir()

        
        # DESTROY ERRORS
        while True:
            try:

                # IF EXISTS
                if cls.base_dir.exists():


                    # MAKE SETTINGS
                    if type in ["settings", 1]:
                        path = cls.base_dir / "settings.json"
                    elif type in ["api", 2]:
                        path = cls.base_dir / "api_keys.json"



                    with open(path, "r") as file:

                        settings = json.load(file)


                        if verbose:
                            console.print(f"Successfully Pulled settings.json from {path}", style="bold green")

                    #console.print(settings)
                    return settings
                

                

                # MAKE PATHS
                else:

                    File_Handling.create_base_dir()
            


            # MAKE JSON
            except FileNotFoundError as e:


                # MAKE SURE BASE IS VALID
                File_Handling.create_base_dir()


                # VERBOSE
                if verbose:
                    console.print(f"[bold red]FileNotFound Error:[yellow] {e}")

                
                # CREATE VARS
                if type in ["settings", 1]:
                    path = cls.base_dir / "settings.json"
                    data = {
                            "iface": "",
                            "subnet": "",
                            "local_ip": "",
                            "captures": ""
                        }
                
                elif type in ["api", 2]:
                    path = cls.base_dir / "api_keys.json"
                    data = {
                            "api_key_discord": ""
                        }



                # PUSH IT 
                with open(path, "w") as file:

                    json.dump(data, file, indent=4)
                

                # PERFECT
                console.print("Successfully created json file", style="bold green")


        
            
            # ERRORS
            except Exception as e:
                console.print(f"[bold red]Exception Error:[yellow] {e}")

                break


    @classmethod
    def push_json(cls, data, type="settings", verbose=True):
        """This method will be used to push info to settings.json"""


        # VARS
        time_stamp = datetime.now().strftime("%m/%d/%Y - %I:%M:%S")


        # MAKE SURE BASE IS VALID
        File_Handling.create_base_dir()



        # DESTROY ERRORS
        while True:
            try:

                # 
                if cls.base_dir.exists():
                    

                    # CREATE VARS
                    if type in ["settings", 1]:
                        path = cls.base_dir / "settings.json"

                    
                    elif type in ["api", 2]:
                        path = cls.base_dir / "api_keys.json"



                    with open(path, "w") as file:

                        json.dump(data, file, indent=4)


                        if verbose:
                            console.print("Successfully pushed settings.json", style="bold green")
                    

                    return



                
                # MAKE DIR
                else:

                    File_Handling.create_base_dir()


                    if verbose:
                        console.print(f"Successfully created dir", style="bold green")
                
            


            except FileNotFoundError as e:


                # MAKE SURE BASE IS VALID
                File_Handling.create_base_dir()


                if verbose:
                    console.print(f"[bold red]FileNotFound Error:[yellow] {e}")

                
                # CREATE VARS
                if type in ["settings", 1]:
                    path = cls.base_dir / "settings.json"
                    data = {
                            "iface": "",
                            "subnet": "",
                            "local_ip": "",
                            "captures": ""
                        }
                
                elif type in ["api", 2]:
                    path = cls.base_dir / "api_keys.json"
                    data = {
                            "api_key_discord": ""
                        }


                # PUSH IT 
                with open(path, "w") as file:

                    json.dump(data, file, indent=4)
                

                # PERFECT
                console.print("Successfully created json file", style="bold green")

                
            
            except Exception as e:
                console.print(f"[bold red]Exception Error:[yellow] {e}")
                
                break




# THIS MODULE FOR THE MOMENT IS THEORETICAL
class Push_Network_Status():
    """This class will be responsible for pushing backend results to the frontend"""




    @classmethod
    def create_base_dir(cls):
        """This method will be responsible for creating base dir"""


        # GET BASE DIR
        cls.base_dir = File_Handling.create_base_dir(verbose=True, get=True)


    @classmethod
    def get_device_info(cls, verbose=True):
        """pull and return json file"""

        

        # CREATE BASE DIR
        cls.base_dir = File_Handling.create_base_dir(verbose=True, get=True)

        

        # LOOP 4 ERROS
        while True:



            try:


                # MAKE SURE BASE EXIST
                if cls.base_dir:                    
    
        
                    # CREATE FILE
                    path = cls.base_dir / "nodes.json"

                    
                    with open(path, "r") as file:
                        data = json.load(file)
                    


                    # RETURN DATA
                    return data
                

                # CREATE BASE DIR
                else:

                    cls.base_dir = File_Handling.create_base_dir(get=True)
            

            except (json.JSONDecodeError, FileExistsError, FileNotFoundError) as e:

                if verbose:
                    console.print(e)
                
                                
                path = cls.base_dir / "nodes.json"

                data = {
                    "summary": {},  
                    "nodes": {}
                }


                with open(path, "w") as file:
                    json.dump(data, file, indent=4)


                    if verbose:
                        console.print(f"File path successfully made", style="bold green")

                
            
            # GENERAL ERRORS
            except Exception as e:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")

                break


    @classmethod
    def push_device_info(cls, summary=False, target_ip=False, target_mac=False, host=False, vendor=False, status=False, verbose=False):
        """This method will be responsible for pushing device info """


        # GET JSON
        data = Push_Network_Status.get_device_info(verbose=True)
        #console.print(data)
        


        # EXAMPLE
        """

        DATA = {
                "summary": {
                    "nodes_online": 12,
                    "nodes_total": 20
                },
                "nodes"{
                    "192.168.1.2" {

                        "target_ip": "192.168.1.2",
                        "target_mac": "01:A1:B2:C3:D4:F6",
                        "host": "nsm-switch",
                        "vendor": "NETGEAR",
                        "status": offline
                        
                        }
                }
        
        
        """

        # REMOVE PREVIOUS INSTANCE


        
        # PUSH IP, MAC, HOST, VENDOR
        if  target_ip:
            data["nodes"][target_ip] = {
                    "target_ip": target_ip,
                    "target_mac": target_mac,
                    "host": host,
                    "vendor": vendor,
                    "status": status
                }
            
        
        # PUSH SUMMARY
        elif summary:
            data["summary"] = summary 



        else:
            data['summary'] = {}
            data["nodes"] = {}

            #console.print("cleaned")



        # CREATE BASE DIR
        File_Handling.create_base_dir(verbose=True, get=True)

        

        # LOOP 4 ERROS
        while True:


            try:


                # MAKE SURE BASE EXIST
                if cls.base_dir:                    
    
        
                    # CREATE FILE
                    path = cls.base_dir / "nodes.json"

                    with open(path, "w") as file:

                        while True:
                            
                            
                            # LOCK IT
                            LOCK.acquire()
       
                            json.dump(data, file, indent=4)
                            
                            # RELEASE IT 
                            LOCK.release()

                            break




                    if verbose:
                        console.print(f"\nSuccessfully updated nodes.json", style="bold green")

                    
                    break
                

                # CREATE BASE DIR
                else:

                    cls.base_dir = File_Handling.create_base_dir(get=True)
            

            # QUICK FIX
            except (KeyError, TypeError) as e:

                if verbose:
                    console.print(e)
                
                data["summary"] = {}
                data["nodes"] = {}
                
                
            # CREATE FILE
            except (json.JSONDecodeError, FileExistsError, FileNotFoundError) as e:
                
                if verbose:
                    console.print(f"[bold red]File not found Error:[bold yellow] {e}")

                
                path = cls.base_dir / "nodes.json"


                data = {
                    "summary": {},  
                    "nodes": {}
                }



                with open(path, "w") as file:

                    while True:
                        
                        # LOCK IT
                        LOCK.acquire()

                        json.dump(data, file, indent=4)
                        
                        # RELEASE IT
                        LOCK.release()

                        break


                    if verbose:
                        console.print(f"File path successfully made", style="bold green")

                
        
            
            # GENERAL ERRORS
            except Exception as e:
                console.print(f"[bold red]push_device_info - Exception Error:[bold yellow] {e}")

                break

    
    @classmethod
    def get_network_summary(cls, delay=5, verbose=False):
        """This method will be responsible for updating the total amount of devices found and online"""


        # VARS
        cls.nodes_online = 0
        cls.nodes_count = 0
        cls.nodes = []

    
        def begin(delay, verbose):


            # IMPORT
            from nsm_utilities import Connection_Handler

 
            # PRINT
            console.print("[bold red][+][bold yellow] Background Thread 1 started")

            
            # LOOP INDEFIENTLY
            while True:


                # CHECK FOR UPDATES
                Connection_Handler.daily_update()

                # RESET
                cls.nodes_online = 0


                # PULL DATA
                data = Push_Network_Status.get_device_info(verbose=True)
                

                # ITER
                for key, value in data["nodes"].items():

                    
                    if verbose:
                        console.print(value["target_ip"]," --> ", value["status"])

                    # GET VARS
                    status = value["status"]
                    target_ip = value["target_ip"]


                    if status == "online":
                        cls.nodes_online += 1
                    
                    
                    
                    # APPEND TOTAL COUNT
                    if target_ip not in cls.nodes:

                        # APPEND
                        cls.nodes.append(target_ip)

                        # ADD
                        cls.nodes_count += 1
                
                
                # SUMMARY
                summary = {
                    "nodes_online": cls.nodes_online,
                    "nodes_total": cls.nodes_count
                }
                

                # PUSH DATA
                Push_Network_Status.push_device_info(summary=summary)
                
                # DELAY
                time.sleep(delay)
            
        

        # START
        threading.Thread(target=begin, args=(5, False), daemon=True).start()
        




# FOR MODULE TESTING
if __name__ == "__main__":
    Push_Network_Status.get_node_count()