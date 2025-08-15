# THIS MODULE WILL BE RESPONSIBLE FOR PERFORMING A PORT SCAN ON NODES


# UI IMPORTS
from rich.console import Console
console = Console()



# NETWORK IMPORTS
import socket


# ETC IMPORTS
from concurrent.futures import ThreadPoolExecutor



class Port_Scanner():
    """This class will allow port scanning on all network wide devices"""



    @classmethod
    def find_open_ports(cls, target_ip, port, timeout):
        """This method will be responsible for finding open ports to then pass to nmap"""
 
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                
                
                # SET TIMEOUT
                s.settimeout(timeout)

                result = s.connect_ex((target_ip, port))

                
                # OPEN
                if result == 0:

                    if cls.verbose:
                        console.print(f"Port: {port} is open")

                    cls.ports['open'].append(port)

                
                # CLOSED
                elif result in [111,113]:

                    if cls.verbose:
                        console.print(f"Port: {port} is closed")


                    cls.ports['closed'].append(port)

                
                # FILTERED
                else:

                    if cls.verbose:
                        console.print(f"Port: {port} is filterd")


                    cls.ports['filterd'].append(port)




        
        except Exception as e:
            if cls.verbose:
                console.print(f"[bold red]Exception Error:[bold yellow] {e}")
            
            cls.ports['filtered'].append(port)

    
    @classmethod
    def threader(cls, target_ip, timeout=2, thread_count=400, verbose=False):
        """This method will be responsible for finding open ports to then pass to nmap"""


        cls.ports = {
            "open": [],
            "filtered": [],
            "closed": []
        }

        cls.verbose = False


        ports = range(1, 1024)



        # THREADED SCAN
        with ThreadPoolExecutor(max_workers=thread_count) as executor:

            # START
            for port in ports:

                executor.submit(Port_Scanner.find_open_ports, target_ip, port, timeout)
        

        # DONE
        console.print(f"Scan completed: {cls.ports}")




if __name__ == "__main__":

    Port_Scanner.threader(target_ip=socket.gethostbyname("linkedin.com"))