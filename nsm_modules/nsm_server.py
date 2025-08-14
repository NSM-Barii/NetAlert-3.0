# THIS MODULE WILL BE A WEB SOCKET THAT WILL AUTO UPDATE THE FRONT END WEB GUI


# UI IMPORTS
from rich.console import Console
console = Console()

# IMPORTS
import os, socket


class Server():
    """This class will be responsible for starting servers"""


    
    @staticmethod
    def begin_web_server(port=8888, dir="../web_modules"):
        """Use this to start front end server"""


        local_ip = "0.0.0.0"


        # START
        #console.print(f"Running front end on: {local_ip}/{port}")

        
        # RUN SERVER
        os.system(f'python -m http.server {port} -d {dir}')