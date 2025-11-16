 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index fc111385ffb4738792c6e226bc3c8d05d6695277..f9ba2d463505dea6fdf715122cef25b87d298397 100644
--- a/README.md
+++ b/README.md
@@ -1,25 +1,29 @@
 # phone-code
 
 ## things you forget because smooth brained
 
 * My editor is sublime text
 
 # GITHUB
 
 cd C:\Users\user\phone-code     # ga naar de projectmap
 
 git add .                       # voeg alle wijzigingen toe
 git commit -m "comment"         # maak een commit
 git push                        # upload naar GitHub
 
 
 # don't forget to
 
 * have pipewire and pulse audio installed and updated
 * make every pie update git and start script on boot
 
 # bugs
 
 * only plays up to 3 then other has buffer issues
 * activate soundcard only after plugging in the jack
 * usb powerdepenency issius (might be fixed with powered usb)
+
+## testing
+
+Run `python -m py_compile multi_play.py` to have Python compile the file and surface any syntax errors without executing the script.
diff --git a/multi_play.py b/multi_play.py
index d9896bf4e4af88e66d4395d7fdc20ad24886672d..042fd211d99ef4ebc5dd301c55049d7f1f6afdb1 100644
--- a/multi_play.py
+++ b/multi_play.py
@@ -1,53 +1,53 @@
-import os
-import subprocess
-import time
-
-# Folder with audio
-SOUND_DIR = "/home/nachtdienst/sound/fixed3"
-
-# Files to play
-sound_files = [
-    "1.wav",
-    "2.wav",
-    "3.wav",
-    "4.wav",
-    "5.wav"
-]
-
-# ALSA device names from: aplay -L
-devices = [
-    "plughw:2,0",
-    "plughw:3,0",
-    "plughw:4,0",
-    "plughw:5,0",
-    "plughw:6,0"
-]
-
-def play_sound(device, filename):
-    path = os.path.join(SOUND_DIR, filename)
-    cmd = [
+from pathlib import Path
+from subprocess import Popen
+from time import sleep
+
+SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
+SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
+DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]
+
+SAMPLE_RATE = 44_100
+CHANNELS = 1
+FORMAT = "S16_LE"
+PERIOD_SIZE = 1024
+BUFFER_SIZE = 4096
+
+
+def build_command(device: str, filename: str) -> list[str]:
+    return [
         "aplay",
-        "-D", device,
-        "-r", "44100",
-        "-c", "1",
-        "--period-size=512",
-        "--buffer-size=2048",
-        path
+        "-D",
+        device,
+        "-f",
+        FORMAT,
+        "-r",
+        str(SAMPLE_RATE),
+        "-c",
+        str(CHANNELS),
+        "--disable-resample",
+        "--disable-format",
+        f"--period-size={PERIOD_SIZE}",
+        f"--buffer-size={BUFFER_SIZE}",
+        str(SOUND_DIR / filename),
     ]
-    print("Running:", " ".join(cmd))
-    return subprocess.Popen(cmd)
 
-processes = []
 
-# Start all playback
-for device, filename in zip(devices, sound_files):
-    print(f"Playing {filename} on {device}")
-    p = play_sound(device, filename)
-    processes.append(p)
-    time.sleep(0.8)
+def main(delay: float = 1.0) -> None:
+    processes: list[tuple[str, str, Popen]] = []
+    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):
+        cmd = build_command(device, filename)
+        print(f"[{idx}/{len(DEVICES)}] Playing {filename} on {device}")
+        print("Running:", " ".join(cmd))
+        processes.append((device, filename, Popen(cmd)))
+        sleep(delay)
+
+    for device, filename, process in processes:
+        return_code = process.wait()
+        if return_code:
+            print(f"Playback on {device} for {filename} exited with {return_code}.")
+
+    print("All playback finished.")
 
-# Wait until all are finished
-for p in processes:
-    p.wait()
 
-print("All playback finished.")
\ No newline at end of file
+if __name__ == "__main__":
+    main()
 
EOF
)

if __name__ == "__main__":
    main()
