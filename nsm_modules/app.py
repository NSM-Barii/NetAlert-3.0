# THIS MODULE WILL BE RESPONSIBLE FOR RUNNING THE WEB SERVER



# UI IMPORTS
from rich.console import Console
console = Console()


# WEB SERVER IMPORTS
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import socket
app = FastAPI()


# FILE IMPORTS
from pathlib import Path



# RUN THIS TO ACTIVATE THE SERVER
#  python -m uvicorn nsm_modules.app:app --reload --host 0.0.0.0 --port 8000




# __MAIN__ IS BELOW


# PATHS
BASE_DIR = Path(__file__).resolve().parents[1]
WEB_SERVER = BASE_DIR / "web_modules"
INDEX = WEB_SERVER / "index.html"


# ALERT THE USER THAT THE SERVER IS WORKING
console.print(
    f"\nServer is hosted from:[bold yellow] {WEB_SERVER}[/bold yellow]  -->  {INDEX}\n",
    style="bold green"
)


# 127.0.0.1/ui
app.mount("/ui", StaticFiles(directory=str(WEB_SERVER), html=True), name="ui")


# THIS IS OPTIONAL TO MAKE ROOT GO TO --> /ui
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")  # note trailing slash


# LOG THE IP THAT CONNECTED
try:
    local_ip = socket.gethostbyname(socket.gethostname())
    console.print(f"[bold green]Web UI:[/bold green] http://{local_ip}:8000/ui/")
except Exception:
    pass



# No __main__ block needed when using uvicorn
