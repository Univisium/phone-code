from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]


def build_command(device: str, filename: str) -> list[str]:
    return [
        "aplay",
        "-D",
        device,
        "-r",
        "44100",
        "-c",
        "1",
        "--period-size=512",
        "--buffer-size=2048",
        str(SOUND_DIR / filename),
    ]


def main(delay: float = 0.5) -> None:
    processes = []
    for device, filename in zip(DEVICES, SOUND_FILES):
        cmd = build_command(device, filename)
        print(f"Playing {filename} on {device}")
        print("Running:", " ".join(cmd))
        processes.append(Popen(cmd))
        sleep(delay)

    for process in processes:
        process.wait()

    print("All playback finished.")


if __name__ == "__main__":
    main()
