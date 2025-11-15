import os
import subprocess
import time

# Folder with audio
SOUND_DIR = "/home/nachtdienst/soun/fixed2"

# Files to play
sound_files = [
    "1.wav",
    "2.wav",
    "3.wav",
    "4.wav",
    "5.wav"
]

# ALSA device names from: aplay -L
devices = [
    "hw:2,0",
    "hw:3,0",
    "hw:4,0",
    "hw:5,0",
    "hw:6,0"
]

def play_sound(device, filename):
    path = os.path.join(SOUND_DIR, filename)
    cmd = ["aplay", "-D", device, path]
    return subprocess.Popen(cmd)

processes = []

# Start all playback
for device, filename in zip(devices, sound_files):
    print(f"Playing {filename} on {device}")
    p = play_sound(device, filename)
    processes.append(p)
    time.sleep(0.2)

# Wait until all are finished
for p in processes:
    p.wait()

print("All playback finished.")