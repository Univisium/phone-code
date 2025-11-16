from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]

SAMPLE_RATE = 44_100
CHANNELS = 1
FORMAT = "S16_LE"
PERIOD_SIZE = 1024
BUFFER_SIZE = 4096


def build_command(device: str, filename: str) -> list[str]:
    return [
           "aplay",
          "-D",
          device,
          "-f",
          FORMAT,
          "-r",
          str(SAMPLE_RATE),
          "-c",
          str(CHANNELS),
          "--disable-resample",
          "--disable-format",
          f"--period-size={PERIOD_SIZE}",
          f"--buffer-size={BUFFER_SIZE}",
          str(SOUND_DIR / filename),
           ]

def main(delay: float = 1.0) -> None:
    processes: list[tuple[str, str, Popen]] = []
    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):
        cmd = build_command(device, filename)
        print(f"[{idx}/{len(DEVICES)}] Playing {filename} on {device}")
        print("Running:", " ".join(cmd))
        processes.append((device, filename, Popen(cmd)))
        sleep(delay)

    for device, filename, process in processes:
        return_code = process.wait()
        if return_code:
            print(f"Playback on {device} for {filename} exited with {return_code}.")

    print("All playback finished.")

if __name__ == "__main__":
    main()