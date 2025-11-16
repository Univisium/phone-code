import wave
from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]

def rainbow_boot_message():
    colors = [
        "\033[31m",   # red
        "\033[33m",   # yellow
        "\033[32m",   # green
        "\033[36m",   # cyan
        "\033[34m",   # blue
        "\033[35m",   # magenta
        "\033[95m",   # light magenta
        "\033[94m",   # light blue
    ]
    text = " multi play system starting "
    rainbow = ""

    for i, char in enumerate(text):
        rainbow += colors[i % len(colors)] + char

    rainbow += "\033[0m"
    print(rainbow)
    print()

# ANSI colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Hardware constraints (None means let ALSA choose)
PERIOD_SIZE: int | None = None
BUFFER_SIZE: int | None = None


def format_from_sample_width(sample_width: int) -> str:
    mapping = {1: "U8", 2: "S16_LE", 3: "S24_LE", 4: "S32_LE"}
    try:
        return mapping[sample_width]
    except KeyError as exc:
        raise ValueError(f"{RED}Unsupported sample width: {sample_width}{RESET}") from exc


def wav_params(path: Path) -> tuple[int, int, str]:
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        format_name = format_from_sample_width(wav_file.getsampwidth())
    return channels, sample_rate, format_name


def build_command(device: str, filename: str, *, include_tuning: bool = True) -> list[str]:
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


def main(delay: float = 1.0) -> None:
    processes: list[dict[str, object]] = []

    print(f"{BLUE}Starting multi playback with debug enabled{RESET}\n")

    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):

        print(f"{YELLOW}[{idx}/{len(DEVICES)}] Preparing {filename} for {device}{RESET}")
        
        cmd = build_command(device, filename, include_tuning=True)
        print(f"{BLUE}Running:{RESET} {' '.join(cmd)}")
        
        tuning_used = any(
            part.startswith(unsupported)
            for part in cmd
            for unsupported in ("--period-size", "--buffer-size")
        )

        processes.append(
            {
                "device": device,
                "filename": filename,
                "cmd": cmd,
                "tuning_used": tuning_used,
                "process": Popen(cmd),
            }
        )

        sleep(delay)
        print()

    print(f"{BLUE}Waiting for all playback to finish...{RESET}\n")

    for proc_info in processes:
        device = proc_info["device"]
        filename = proc_info["filename"]
        process: Popen = proc_info["process"]  # type: ignore
        tuning_used = proc_info["tuning_used"]

        return_code = process.wait()

        if return_code and tuning_used:
            print(f"{RED}Playback on {device} for {filename} failed with {return_code}{RESET}")
            print(f"{YELLOW}Retrying without period or buffer tuning{RESET}")
            
            fallback_cmd = build_command(device, filename, include_tuning=False)
            print(f"{BLUE}Retry running:{RESET} {' '.join(fallback_cmd)}")

            retry_code = Popen(fallback_cmd).wait()
            if retry_code:
                print(
                    f"{RED}Fallback playback on {device} for {filename} exited with {retry_code}{RESET}"
                )
            else:
                print(
                    f"{GREEN}Fallback playback on {device} for {filename} succeeded{RESET}"
                )

        elif return_code:
            print(f"{RED}Playback on {device} for {filename} exited with code {return_code}{RESET}")
        else:
            print(f"{GREEN}Playback OK on {device} for {filename}{RESET}")

    print(f"\n{GREEN}All playback attempts finished.{RESET}")


if __name__ == "__main__":
    main()
