# THIS MODULE WILL BE FOR UTILITIES



# UI IMPORTS
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
console = Console()

# ETC IMPORTS
import sqlite3
from datetime import datetime



# NSM IMPORTS
from nsm_files import File_Handling




class Utilities():
    """This will be responsible for common utilities"""


    def __init__(self):
        pass



    @classmethod
    def push_sql_db(cls, proto, ip_src, ip_dst, port_src, port_dst, pkt_ttl, pkt_len, verbose=True):
        """This method will be used to push and pull info from the SQL DB"""


        # GET SQL PATH
        sql = File_Handling.path_for_sql(get=True)


        # CREATE DB PATH 
        path = sql / "network_traffic_all.db"



        # GET TIMESTAMP
        time_stamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S")




        # CREATE DATABASE CONNECTION
        with sqlite3.connect(f"network_traffic_all.db") as conn:


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




