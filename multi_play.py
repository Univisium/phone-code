import wave
from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]

DEBUG = True

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[94m"
RESET = "\033[0m"

PERIOD_SIZE = None
BUFFER_SIZE = None

def debug_print(msg: str) -> None:
    if DEBUG:
        print(msg)

def format_from_sample_width(sw: int) -> str:
    mapping = {1: "U8", 2: "S16_LE", 3: "S24_LE", 4: "S32_LE"}
    return mapping.get(sw) or (_ for _ in ()).throw(ValueError(f"{RED}Unsupported sample width {sw}{RESET}"))

def wav_params(path: Path):
    with wave.open(str(path), "rb") as f:
        return f.getnchannels(), f.getframerate(), format_from_sample_width(f.getsampwidth())

def build_command(device: str, filename: str, include_tuning=True):
    channels, sample_rate, format_name = wav_params(SOUND_DIR / filename)

    cmd = [
        "aplay",
        "-D", device,
        "-f", format_name,
        "-r", str(sample_rate),
        "-c", str(channels),
    ]

    if include_tuning and PERIOD_SIZE is not None:
        cmd.append(f"--period-size={PERIOD_SIZE}")

    if include_tuning and BUFFER_SIZE is not None:
        cmd.append(f"--buffer-size={BUFFER_SIZE}")

    cmd.append(str(SOUND_DIR / filename))

    return cmd

def main(delay: float = 0.5):
    debug_print(f"{BLUE}Starting parallel multi playback{RESET}\n")

    processes = []

    # Start all processes immediately (parallel playback)
    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):

        debug_print(f"{YELLOW}[{idx}/{len(DEVICES)}] Starting {filename} on {device}{RESET}")

        cmd = build_command(device, filename, include_tuning=True)
        debug_print(f"{BLUE}Running:{RESET} {' '.join(cmd)}")

        proc = Popen(cmd)

        processes.append({
            "device": device,
            "filename": filename,
            "process": proc,
            "tuning_used": PERIOD_SIZE is not None or BUFFER_SIZE is not None,
        })

        sleep(delay)

    # Now wait for all and count results
    debug_print(f"\n{BLUE}Waiting for all playback to finish...{RESET}\n")

    success_count = 0
    fail_count = 0

    for info in processes:
        device = info["device"]
        filename = info["filename"]
        proc = info["process"]
        tuning_used = info["tuning_used"]

        return_code = proc.wait()

        if return_code == 0:
            success_count += 1
            debug_print(f"{GREEN}OK on {device} for {filename}{RESET}")
        else:
            fail_count += 1
            debug_print(f"{RED}FAILED on {device} for {filename} code {return_code}{RESET}")

    print(f"\n{GREEN}{success_count} played successfully{RESET}, {RED}{fail_count} failed{RESET}")

if __name__ == "__main__":
    main()
