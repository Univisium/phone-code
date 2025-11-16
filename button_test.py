import RPi.GPIO as GPIO
from subprocess import Popen
import time

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Waiting for button press...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed")
            Popen([
                "python3",
                "multi_play.py",
                "--button",
                "--device", "plughw:3,0",
                "--sound", "/home/nachtdienst/sound/Button.wav"
            ])
            time.sleep(0.3)  # debounce
        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
