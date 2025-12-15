#  GNU nano 8.7                                                                               New Buffer *                                                                                       
import subprocess; from pathlib import Path


path = str(Path(__file__).parent / "output.mp3" )

import sys
import subprocess

audio_file = sys.argv[1]
subprocess.run([
    "mpv", "--no-video", "--volume=100", audio_file
])
print("back ran")