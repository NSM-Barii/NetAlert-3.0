# THIS MODULE WILL BE A WEB SOCKET THAT WILL AUTO UPDATE THE FRONT END WEB GUI


# UI IMPORTS
from rich.console import Console
console = Console()


# NSM IMPORTS
from nsm_utilities import Connection_Handler


# IMPORTS
import os, socket


class Server():
    """This class will be responsible for starting servers"""


    
    @staticmethod
    def begin_web_server(iface, port=8888, dir="../web_modules"):
        """Use this to start front end server"""


        local_ip = Connection_Handler.get_local_ip(iface=iface)


        # START
        console.print(f"Running front end on: {local_ip}/{port}")

        
        # RUN SERVER
        os.system(f'python -m http.server -b {local_ip} {port} -d {dir}')