import os
import subprocess
import time

# Folder with audio
SOUND_DIR = "/home/nachtdienst/sound/fixed"

# Files to play
sound_files = [
    "1.wav",
    "2.wav",
    "3.wav",
    "4.wav",
    "5.wav"
]

# PulseAudio sink names from `pactl list short sinks`
sinks = [
    "alsa_output.platform-fe00b840.mailbox.stereo-fallback",
    "alsa_output.usb-Generic_AB13X_USB_Audio_20210926172016-00.analog-stereo",
    "alsa_output.usb-Generic_AB13X_USB_Audio_20210926172016-00.analog-stereo.2",
    "alsa_output.usb-Generic_AB13X_USB_Audio_20210926172016-00.analog-stereo.3",
    "alsa_output.usb-Generic_AB13X_USB_Audio_20210926172016-00.analog-stereo.4"
]

def play_sound(sink, filename):
    path = os.path.join(SOUND_DIR, filename)
    cmd = ["paplay", "--device", sink, path]
    return subprocess.Popen(cmd)

processes = []

# Start all playback
for sink, filename in zip(sinks, sound_files):
    print(f"Playing {filename} on {sink}")
    p = play_sound(sink, filename)
    processes.append(p)
    time.sleep(0.2)

# Wait until all are finished
for p in processes:
    p.wait()

print("All playback finished.")
