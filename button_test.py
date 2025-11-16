import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# PUD_UP means the pin is normally HIGH, the button makes it LOW

print("Waiting for button press on GPIO17")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("Button pressed!")
            time.sleep(0.2)  # debounce delay
        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
