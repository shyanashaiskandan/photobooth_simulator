import threading
import time
import RPi.GPIO as GPIO
import requests

BUTTON_PIN = 26  # Ensure this matches your hardware configuration

def monitor_button():
    # Set up the GPIO for the button; use an internal pull-down resistor.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            try:
                # Send a POST request to the local server to trigger 'start'
                requests.post("http://127.0.0.1:8000/", data={"action": "start"})
                print("Push button pressed: Triggered photobooth start")
            except Exception as e:
                print("Error sending POST request:", e)
            # Debounce delay
            time.sleep(2)
        time.sleep(0.1)

def start_listener():
    thread = threading.Thread(target=monitor_button, daemon=True)
    thread.start()