import wave
from pathlib import Path
from subprocess import Popen
from time import sleep

SOUND_DIR = Path("/home/nachtdienst/sound/fixed3")
SOUND_FILES = ["1.wav", "2.wav", "3.wav", "4.wav", "5.wav"]
DEVICES = ["plughw:2,0", "plughw:3,0", "plughw:4,0", "plughw:5,0", "plughw:6,0"]

# Hardware constraints (set to None to let aplay choose automatically)
PERIOD_SIZE: int | None = None
BUFFER_SIZE: int | None = None


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


def build_command(device: str, filename: str, *, include_tuning: bool = True) -> list[str]:
    channels, sample_rate, format_name = wav_params(SOUND_DIR / filename)
    cmd = [
        "aplay",
        "-D",
        device,
        "-f",
        format_name,
        "-r",
        str(sample_rate),
        "-c",
        str(channels),
    ]

    if include_tuning and PERIOD_SIZE is not None:
        cmd.append(f"--period-size={PERIOD_SIZE}")
    if include_tuning and BUFFER_SIZE is not None:
        cmd.append(f"--buffer-size={BUFFER_SIZE}")

    cmd.append(str(SOUND_DIR / filename))
    return cmd

def main(delay: float = 1.0) -> None:
    processes: list[dict[str, object]] = []
    for idx, (device, filename) in enumerate(zip(DEVICES, SOUND_FILES), start=1):
        cmd = build_command(device, filename, include_tuning=True)
        print(f"[{idx}/{len(DEVICES)}] Preparing {filename} for {device}")
        print("Running:", " ".join(cmd))
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

    for proc_info in processes:
        device = proc_info["device"]
        filename = proc_info["filename"]
        process: Popen = proc_info["process"]  # type: ignore[assignment]
        tuning_used = proc_info["tuning_used"]

        return_code = process.wait()
        if return_code and tuning_used:
            print(
                f"Playback on {device} for {filename} failed with {return_code}; "
                "retrying without period/buffer hints."
            )
            fallback_cmd = build_command(device, filename, include_tuning=False)
            print("Retry running:", " ".join(fallback_cmd))
            retry_code = Popen(fallback_cmd).wait()
            if retry_code:
                print(
                    f"Fallback playback on {device} for {filename} "
                    f"exited with {retry_code}."
                )
        elif return_code:
            print(f"Playback on {device} for {filename} exited with {return_code}.")

    print("All playback attempts finished.")

if __name__ == "__main__":
    main()
