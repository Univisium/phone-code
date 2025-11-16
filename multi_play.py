import wave
from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]

# Hardware constraints
PERIOD_SIZE = 1024
BUFFER_SIZE = 4096


def format_from_sample_width(sample_width: int) -> str:
    mapping = {1: "U8", 2: "S16_LE", 3: "S24_LE", 4: "S32_LE"}
    try:
        return mapping[sample_width]
    except KeyError as exc:
        raise ValueError(f"Unsupported sample width: {sample_width}") from exc


def wav_params(path: Path) -> tuple[int, int, str]:
    with wave.open(path, "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        format_name = format_from_sample_width(wav_file.getsampwidth())
    return channels, sample_rate, format_name


def build_command(device: str, filename: str) -> list[str]:
    channels, sample_rate, format_name = wav_params(SOUND_DIR / filename)
    return [
        "aplay",
        "-D",
        device,
        "-f",
        format_name,
        "-r",
        str(sample_rate),
        "-c",
        str(channels),
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
