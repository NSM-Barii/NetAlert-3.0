# THIS MODULE WILL BE A WEB SOCKET THAT WILL AUTO UPDATE THE FRONT END WEB GUI


# UI IMPORTS
from rich.console import Console
console = Console()


# NSM IMPORTS
from nsm_utilities import Connection_Handler


# IMPORTS
import os, socket, time


class Server():
    """This class will be responsible for starting servers"""


    
    @staticmethod
    def begin_web_server(local_ip, iface=False, port=8888, dir="../web_modules"):
        """Use this to start front end server"""


        time.sleep(0.2)


        #local_ip = Connection_Handler.get_local_ip(iface=iface)

        #local_ip = console.input("Enter local ip: ") if local_ip == "0.0.0.0" else local_ip

        #local_ip = "192.168.1.49"
 

        # START
        #console.print(f"Running front end on: {local_ip}/{port}")

        
        # RUN SERVER
        if os.name == "posix":
            
            #console.print("[bold green]Run this if your new --> [bold yellow]cd web_modules - ln -s ../../.data/netalert3/nodes.json . ")
            os.system(f"python3 -m http.server -b {local_ip} {port} -d {dir} 2>/dev/null")
                    #{local_ip} {port} -d {dir} 2>/dev/null

            
            # CREATE SYSLINK
            #console.print("[bold green]Run this if your new --> [bold yellow]cd web_modules - ln -s ../../.data/netalert3/nodes.json . ")
            #os.symlink(src="Documents/nsm_tools/.data/netalert3/nodes.json", dst="Documents/nsm_tools/netalert3/web_modules/nodes.json")
            #os.system("ln -s ../../.data/netalert3/nodes.json ~/Documents/nsm_tools/netalert3/web_modules/nodes.json")

        # WINDOWS
        else:
            os.system(f"python -m http.server -d {dir}")