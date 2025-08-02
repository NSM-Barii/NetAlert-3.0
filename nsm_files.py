# THIS MODULE WILL BE FOR FILE HANDLING




# UI IMPORTS
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.console import Console
console = Console()


# ETC IMPORTS
import os
from datetime import datetime


# FILE IMPORTS
from pathlib import Path
import json



class File_Handling():
    """This method will be responsible for file creation and handling"""


    def __init__(self):
        pass


    
    @classmethod
    def create_base_dir(cls, verbose=False):
        """This single method will be responsible soley for creating def path"""

        
        # TRY
        try:
    
            # FOR SUDO PATH
            USER_HOME = Path(os.getenv("SUDO_USER", "home") and f"/home/{os.getenv("SUDO_USER")}") or Path.home()
            cls.base_dir = USER_HOME / "Documents" / "nsm_tools" / ".data" / "netalert3"

        

        # DEF BACK
        except Exception as e:

            if verbose:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")


            # FALL BACK TO NON SUDO PATH
            cls.base_dir = Path.home() / "Documents" / "nsm_tools" / ".data" / "netalert3" 
        

        # CREATE BASE IN CASE
        cls.base_dir.mkdir(exist_ok=True, parents=True)


        # NOTIFY
        if verbose:
            console.print("base_dir set", style="bold green")
            


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
    def get_json(cls, verbose=True):
        """This will pull and return json info"""


        # MAKE SURE BASE IS VALID
        File_Handling.create_base_dir()

        
        # DESTROY ERRORS
        while True:
            try:

                # IF EXISTS
                if cls.base_dir.exists():


                    # MAKE SETTINGS
                    path = cls.base_dir / "settings.json"


                    with open(path, "r") as file:

                        settings = json.load(file)


                        if verbose:
                            console.print(f"Successfully Pulled settings.json from {path}", style="bold green")


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
                path = cls.base_dir / "settings.json"
                data = {
                        "iface": "",
                        "captures": ""
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
    def push_json(cls, data, verbose=True):
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
                    

                    # VARS
                    path = cls.base_dir / "settings.json"

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
                path = cls.base_dir / "settings.json"
                data = {
                        "iface": "",
                        "captures": ""
                    }


                # PUSH IT 
                with open(path, "w") as file:

                    json.dump(data, file, indent=4)
                

                # PERFECT
                console.print("Successfully created json file", style="bold green")

                
            
            except Exception as e:
                console.print(f"[bold red]Exception Error:[yellow] {e}")
                
                break