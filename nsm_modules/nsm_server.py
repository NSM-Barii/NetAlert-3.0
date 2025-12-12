from rich.console import Console
console = Console()

from nsm_utilities import Connection_Handler

import os, socket, time
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import json


class YodaHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/nodes.json':
            try:
                data = {"nodes": Connection_Handler.nodes}

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
            super().do_GET()


class Server():

    @staticmethod
    def begin_web_server(local_ip, iface=False, port=8000, dir="../web_modules"):

        time.sleep(0.2)

        web_dir = str(Path(__file__).parent.parent / "web_modules")

        console.print(f"[bold green][+] Starting YODA server on port {port}")
        console.print(f"[bold cyan]    Access at: http://localhost:{port}/yoda.html")
        console.print(f"[bold yellow]    Serving live data from Connection_Handler.nodes")

        handler = lambda *args, **kwargs: YodaHandler(*args, directory=web_dir, **kwargs)

        server = HTTPServer(('0.0.0.0', port), handler)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Server stopped")