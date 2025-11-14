"""Play WAV files on multiple ALSA devices simultaneously.

This script is designed for Raspberry Pi setups with multiple USB sound cards
where each card should play a different WAV file.  It acts as a convenience
wrapper around the `aplay` command that ships with ALSA, spawning one process
per output device.

Usage examples
--------------

List ALSA playback devices:

    python3 multi_play.py --list-devices

Play files on specific devices:

    python3 multi_play.py \
        --map hw:Device1=/home/pi/sounds/left.wav \
        --map hw:Device2=/home/pi/sounds/right.wav

The device identifiers must match what `aplay -L` reports.  You can also create
an INI-style configuration file (see ``--config``) so you don't need to repeat
mappings on the command line.
"""

from __future__ import annotations

import argparse
import configparser
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def list_devices() -> int:
    """Print playback devices using ``aplay -L``.

    Returns the exit code from ``aplay``.  A non-zero exit code usually means
    that ALSA is not available or ``aplay`` is not installed.
    """

    try:
        result = subprocess.run(["aplay", "-L"], check=False)
        return result.returncode
    except FileNotFoundError:
        print(
            "Error: `aplay` command not found. Install the alsa-utils package.",
            file=sys.stderr,
        )
        return 1


def parse_mapping_arg(values: Iterable[str]) -> Dict[str, Path]:
    """Parse ``--map`` arguments of the form ``device=path``.

    Args:
        values: Iterable containing strings in the ``device=path`` format.

    Returns:
        Dictionary mapping device names to ``Path`` objects.
    """

    mapping: Dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(
                f"Invalid map value '{value}'. Expected format device=path."
            )
        device, path_str = value.split("=", 1)
        path = Path(path_str).expanduser().resolve()
        mapping[device] = path
    return mapping


def load_config(path: Path) -> Dict[str, Path]:
    """Load device/file mappings from an INI-style configuration file."""

    config = configparser.ConfigParser()
    with path.open("r", encoding="utf-8") as f:
        config.read_file(f)

    mapping: Dict[str, Path] = {}
    for section in config.sections():
        for device, file_path in config.items(section):
            mapping[device] = Path(file_path).expanduser().resolve()
    return mapping


def spawn_aplay_processes(mappings: Dict[str, Path]) -> List[subprocess.Popen]:
    """Spawn one ``aplay`` process per mapping."""

    processes: List[subprocess.Popen] = []
    for device, wav_path in mappings.items():
        if not wav_path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")

        cmd = ["aplay", "-D", device, str(wav_path)]
        print(f"Launching: {' '.join(shlex.quote(arg) for arg in cmd)}")
        try:
            proc = subprocess.Popen(cmd)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "`aplay` command not found. Install the alsa-utils package."
            ) from exc
        processes.append(proc)
    return processes


def wait_for_processes(processes: Iterable[subprocess.Popen]) -> Tuple[int, List[int]]:
    """Wait for all ``aplay`` processes to finish.

    Returns a tuple of overall exit code (0 if all succeeded) and a list of
    individual return codes.
    """

    return_codes: List[int] = []
    overall_code = 0
    for proc in processes:
        rc = proc.wait()
        return_codes.append(rc)
        if rc != 0:
            overall_code = 1
    return overall_code, return_codes


def merge_mappings(primary: Dict[str, Path], secondary: Dict[str, Path]) -> Dict[str, Path]:
    """Merge device mappings, with ``primary`` taking precedence."""

    merged = dict(secondary)
    merged.update(primary)
    return merged


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Play multiple WAV files at the same time on different ALSA devices.\n"
            "Each --map option should look like 'device=file.wav'.\n"
            "Use --list-devices to see available outputs."
        )
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List ALSA playback devices using `aplay -L` and exit.",
    )
    parser.add_argument(
        "--map",
        dest="map_entries",
        metavar="DEVICE=FILE",
        action="append",
        default=[],
        help="Assign a WAV file to play on a device. Repeat for each output.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help=(
            "Path to an INI file defining device mappings. Each entry should be\n"
            "formatted as device=path under any section. Command line mappings\n"
            "override entries defined in the configuration file."
        ),
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.list_devices:
        return list_devices()

    config_mapping: Dict[str, Path] = {}
    if args.config:
        config_path = args.config.expanduser().resolve()
        if not config_path.exists():
            parser.error(f"Configuration file not found: {config_path}")
        config_mapping = load_config(config_path)

    cli_mapping = parse_mapping_arg(args.map_entries)
    mappings = merge_mappings(cli_mapping, config_mapping)

    if not mappings:
        parser.error("No device/file mappings provided. Use --map or --config.")

    processes = spawn_aplay_processes(mappings)
    overall_code, return_codes = wait_for_processes(processes)

    if overall_code != 0:
        failed = [str(code) for code in return_codes if code != 0]
        print(
            "One or more playback commands failed with exit codes: " + ", ".join(failed),
            file=sys.stderr,
        )
    return overall_code


if __name__ == "__main__":
    raise SystemExit(main())
