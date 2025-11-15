import os
import subprocess
import time

# Directory containing your audio files
SOUND_DIR = "/home/nachtdienst/sound/fixed"

# List of sound files (match these to your telephone audio)
sound_files = [
    "1.wav",
    "2.wav",
    "3.wav",
    "4.wav",
    "5.wav",
    # add more when your powered hub arrives:
    # "phone5.wav",
    # "phone6.wav",
    # ...
]

# The ALSA card numbers you want to use
cards = [2, 3, 4, 5, 6]   # Update these when more USB cards appear

def play_sound(card, filename):
    """Start aplay on the given ALSA card."""
    path = os.path.join(SOUND_DIR, filename)
    cmd = ["aplay", "-D", f"plughw:{card},0", path]
    return subprocess.Popen(cmd)