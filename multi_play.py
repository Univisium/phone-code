import os
import subprocess
import time

# Folder with audio
SOUND_DIR = "/home/nachtdienst/sound/fixed3"

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
    "plughw:2,0",
    "plughw:3,0",
    "plughw:4,0",
    "plughw:5,0",
    "plughw:6,0"
]

def play_sound(device, filename):
    path = os.path.join(SOUND_DIR, filename)
    cmd = [
        "aplay",
        "-D", device,
        "-r", "44100",
        "-c", "1",
        "--period-size=512",
        "--buffer-size=2048",
        path
    ]
    print("Running:", " ".join(cmd))
    return subprocess.Popen(cmd)

processes = []

# Start all playback
for device, filename in zip(devices, sound_files):
    print(f"Playing {filename} on {device}")
    p = play_sound(device, filename)
    processes.append(p)
    time.sleep(0.8)

# Wait until all are finished
for p in processes:
    p.wait()

print("All playback finished.")