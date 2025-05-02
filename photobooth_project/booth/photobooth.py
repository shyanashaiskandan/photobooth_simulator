import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import os
import boto3
import yagmail
from PIL import Image  # For cropping

# --- Configuration Variables ---
LOG_FILE_NAME = "/home/shyana/camera/photo_logs.txt"
LOCAL_PHOTO_DIR = "/home/shyana/camera/"
RED_LED_PIN = 17
BLUE_LED_PIN = 27
# Note: We no longer use BUTTON_PIN here since a separate listener handles that

S3_BUCKET = "ss-photobooth-uploads"  # 🔹 Replace with your actual AWS S3 bucket name
S3_REGION = "us-east-2"         # 🔹 Change if needed

# --- AWS S3 Client ---
s3 = boto3.client("s3")

# --- Helper Functions ---
def flash_led(pin, times, delay):
    for _ in range(times):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(delay)


def take_photo(camera):
    """
    Capture a photo and return only the filename.
    (The full path is built using LOCAL_PHOTO_DIR.)
    """
    file_name = "img_" + str(int(time.time())) + ".jpg"
    full_path = os.path.join(LOCAL_PHOTO_DIR, file_name)
    camera.capture(full_path)
    return file_name

def update_photo_log_file(photo_file_name):
    with open(LOG_FILE_NAME, "a") as f:
        f.write(photo_file_name + "\n")

def capture_photos():
    """
    Process:
      1. Flash red LED 3 times (once every second).
      2. For 3 rounds: flash blue LED, capture a photo, then wait 5 seconds.
      3. Flash red LED 3 times at the end.
    Returns a list of filenames (not full paths).
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(BLUE_LED_PIN, GPIO.LOW)

    if os.path.exists(LOG_FILE_NAME):
        os.remove(LOG_FILE_NAME)

    camera = PiCamera()
    camera.resolution = (720, 480)
    camera.rotation = 180
    time.sleep(2)  # Warm-up time

    flash_led(RED_LED_PIN, 3, 1)

    photo_files = []
    for i in range(3):
        flash_led(BLUE_LED_PIN, 1, 0.5)
        file_name = take_photo(camera)
        update_photo_log_file(file_name)
        photo_files.append(file_name)
        time.sleep(5)

    flash_led(RED_LED_PIN, 3, 1)
    camera.close()
    GPIO.cleanup()
    return photo_files

def crop_image_center(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        new_edge = min(width, height)
        left = (width - new_edge) / 2
        top = (height - new_edge) / 2
        right = (width + new_edge) / 2
        bottom = (height + new_edge) / 2
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(image_path)

def upload_to_s3(file_path):
    file_name = os.path.basename(file_path)
    s3_destination = f"uploads/{file_name}"
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_destination)
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_destination}"
        return file_url
    except Exception as e:
        print(f"S3 Upload Failed: {e}")
        return None

def send_email_with_photos(yagmail_client, email_address, photo_urls):
    email_content = "Thank you for using our Photo Booth! Here are your photos:\n\n" + "\n".join(photo_urls)
    yagmail_client.send(
        to=email_address,
        subject="Your Photo Booth Pictures 🎉",
        contents=email_content
    )

def return_prompt(photo_files):
    """
    Returns a default message for the photo prompt.
    """
    return "Your night was filled with unforgettable moments!"
