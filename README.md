# phone-code

This repository contains a simple Python utility that helps you play different
WAV files on multiple USB sound cards connected to a Raspberry Pi.  The script
wraps ALSA's `aplay` command so you can trigger all outputs at the same time.

## Requirements

* Raspberry Pi (or any Linux machine with ALSA support)
* Python 3.9 or newer
* `alsa-utils` package (provides the `aplay` command)

## Installation

Clone the repository to your Raspberry Pi and install the requirements:

```bash
sudo apt-get update
sudo apt-get install -y alsa-utils
```

### Python dependencies

You do **not** need to run `pip install` for this project.  The script relies
entirely on Python's standard library modules (`argparse`, `configparser`,
`pathlib`, `subprocess`, etc.), so a stock Python 3.9+ installation already has
everything that is required.  Just make sure the system package `alsa-utils`
is present so the `aplay` executable is available.

## Usage

1. List available ALSA playback devices so you know the identifiers to use:

    ```bash
    python3 multi_play.py --list-devices
    ```

2. Play WAV files on different devices simultaneously:

    ```bash
    python3 multi_play.py \
      --map hw:Device1=/home/pi/sounds/track1.wav \
      --map hw:Device2=/home/pi/sounds/track2.wav
    ```

   Replace `hw:Device1` and `hw:Device2` with the names reported by
   `aplay -L`, and update the paths to point to your WAV files.

3. (Optional) Store your mappings in a configuration file to avoid repeating
   them on the command line.  Create a file like `config.ini`:

    ```ini
    [soundcards]
    hw:Device1 = /home/pi/sounds/track1.wav
    hw:Device2 = /home/pi/sounds/track2.wav
    ```

   Then run:

    ```bash
    python3 multi_play.py --config config.ini
    ```

Command line options always override values defined in the configuration file.

## Troubleshooting

* If you see `aplay: command not found`, ensure that the `alsa-utils` package
  is installed.
* Confirm that each WAV file exists and uses a sample rate supported by the
  target sound card.
* If playback starts at different times, verify that your WAV files have the
  same duration; the script launches all `aplay` processes concurrently, but
  ALSA cannot compensate for length differences.
