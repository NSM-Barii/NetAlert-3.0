# THIS MODULE WILL BE A WEB SOCKET THAT WILL AUTO UPDATE THE FRONT END WEB GUI


# UI IMPORTS
from rich.console import Console
console = Console()


# NSM IMPORTS
from nsm_utilities import Connection_Handler


# IMPORTS
import os, socket, time
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import json


class YodaHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves static files + live node data from memory"""

    def do_GET(self):
        # Intercept /nodes.json requests and serve data directly from Connection_Handler
        if self.path == '/nodes.json':
            try:
                # Get live data from Connection_Handler.nodes
                data = {"nodes": Connection_Handler.nodes}

                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            except Exception as e:
                console.print(f"[bold red]Error serving nodes.json:[bold yellow] {e}")
                self.send_error(500, str(e))
        else:
            # Serve static files normally (HTML, CSS, JS)
            super().do_GET()


class Server():
    """This class will be responsible for starting servers"""


    @staticmethod
    def begin_web_server(local_ip, iface=False, port=8000, dir="../web_modules"):
        """Use this to start front end server with live data"""

        time.sleep(0.2)

        # Get web directory path
        web_dir = Path(__file__).parent.parent / "web_modules"

        console.print(f"[bold green][+] Starting YODA server on port {port}")
        console.print(f"[bold cyan]    Access at: http://localhost:{port}/yoda.html")
        console.print(f"[bold yellow]    Serving live data from Connection_Handler.nodes")

        # Change to web directory so static files are served correctly
        os.chdir(str(web_dir))

        # Start server with custom handler
        server = HTTPServer(('0.0.0.0', port), YodaHandler)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Server stopped")