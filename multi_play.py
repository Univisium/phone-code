import wave
import argparse

from pathlib import Path
from subprocess import Popen, PIPE
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


def summarize_alsa_error(stderr: str) -> str:
    if not stderr:
        return "SHITTT Unknown error"

    lines = stderr.strip().splitlines()

    for line in lines:
        if "Unable to install hw params" in line:
            return "Unable to install hw params | device said NOPE"
        if "No such file or directory" in line:
            return "Device not found | Where is soundcard?"
        if "busy" in line.lower():
            return "Device is busy | soundcard already taking a shit"
        if "broken pipe" in line.lower():
            return "Device disconnected | plug it back in UwU"
        if "invalid argument" in line.lower():
            return "invalid argument | You asked ALSA to do something that literally makes no sense"

    return lines[0] if lines else "Unknown ALSA error"


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

def play_single_sound(device: str, sound_path: str):
    # Stop whatever is playing on this device
    import os
    os.system(f"pkill -f 'aplay -D {device}'")

    channels, sample_rate, fmt = wav_params(Path(sound_path))

    cmd = [
        "aplay",
        "-D", device,
        "-f", fmt,
        "-r", str(sample_rate),
        "-c", str(channels),
        sound_path
    ]

    print(f"{GREEN}Playing single sound on {device}{RESET}")
    print(" ".join(cmd))

    Popen(cmd)



def main(delay: float = 0.005):
    debug_print(f"{BLUE}Starting parallel multi playback{RESET}\n")

    processes = []
    success_count = 0
    fail_count = 0

    # Start all processes immediately (parallel playback)
    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):

        debug_print(f"{YELLOW}[{idx}/5] Preparing {filename} for {device}{RESET}")

        cmd = build_command(device, filename, include_tuning=True)
        debug_print(f"{BLUE}Running:{RESET} {' '.join(cmd)}")

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)

        # Check if it started playing
        sleep(0.1)
        initial_state = proc.poll()

        if initial_state is None:
            print(f"{GREEN}[{idx}/5] {filename} started playing on {device}{RESET}")
        else:
            # Read stderr NOW so we can summarize immediately
            stderr_now = proc.stderr.read() if proc.stderr else ""
            error_summary = summarize_alsa_error(stderr_now)
            print(f"{RED}[{idx}/5] {filename} failed on {device}{RESET} ({error_summary})")
            fail_count += 1

        processes.append(
            {
                "device": device,
                "filename": filename,
                "process": proc,
            }
        )

        sleep(delay)
        debug_print("")

    # Now wait for all and count remaining results
    debug_print(f"\n{BLUE}Waiting for expo to finish...{RESET}\n")

    for info in processes:
        device = info["device"]
        filename = info["filename"]
        proc = info["process"]

        return_code = proc.wait()

        if return_code == 0:
            success_count += 1
        else:
            # Already printed reason earlier – no need to show again
            pass

    print(f"\n{GREEN}{success_count} played successfully{RESET}, {RED}{fail_count} failed{RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--button", action="store_true", help="Trigger single sound through button")
    parser.add_argument("--device", type=str, help="ALSA device")
    parser.add_argument("--sound", type=str, help="Sound file path")
    args = parser.parse_args()

    # Button mode: plays one sound and exits
    if args.button:
        play_single_sound(
            args.device or "plughw:3,0",
            args.sound or "/home/nachtdienst/sound/Button.wav"
        )
    else:
        # Normal multi-playback mode
        main()