# Import libraries
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import os
import yagmail
import boto3

# Pin configuration variables and paths
LOG_FILE_NAME = "/home/shyana/camera/photo_logs.txt"
PIR_PIN = 4
RED_LED_PIN = 17
BLUE_LED_PIN = 27
BUTTON_PIN = 26
LOCAL_PHOTO_DIR = "/home/shyana/camera/"
S3_BUCKET = "ss-photobooth-uploads" # 🔹 Replace with your actual AWS S3 bucket name
S3_REGION = "us-east-2"  # 🔹 Change this if needed

# Function to flash an LED a specified number of times
def flash_led(pin, times, delay):
    for _ in range(times):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(delay)

# Function to capture a photo and return file path
def take_photo(camera):
    file_name = LOCAL_PHOTO_DIR + "img_" + str(int(time.time())) + ".jpg"
    camera.capture(file_name)
    return file_name

# Function to update log file with file name of newly taken photo
def update_photo_log_file(photo_file_name):
    with open(LOG_FILE_NAME, "a") as f:
        f.write(photo_file_name)
        f.write("\n")

# Initialize AWS S3 Client
s3 = boto3.client("s3")

def upload_to_s3(file_path):
    """Uploads a file to S3 and returns the file URL."""
    file_name = os.path.basename(file_path)
    s3_destination = f"uploads/{file_name}"  # 🔹 Uploads to 'uploads/' folder in S3

    try:
        s3.upload_file(file_path, S3_BUCKET, s3_destination)
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_destination}"
        print(f"✅ Uploaded to S3: {file_url}")
        return file_url
    except Exception as e:
        print(f"❌ S3 Upload Failed: {e}")
        return None

# Function to send email with S3 photo links
def send_email_with_photo(yagmail_client, file_name):
    yagmail_client.send(to='shyana.shais@gmail.com',
         subject="A new photo has been taken!",
         contents="Thank you for working with us! We hope you enjoy your photos!",
         attachments=file_name)

# Setting up camera
camera = PiCamera()
camera.resolution = (720, 480)
camera.rotation = 180
print("Waiting 2 seconds to initialize the camera...")
time.sleep(2)
print("Camera is ready!")

# Setting up GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.output(RED_LED_PIN, GPIO.LOW)
GPIO.output(BLUE_LED_PIN, GPIO.LOW)
print("GPIOs have been set up")

# Removing log file if it already exists
if os.path.exists(LOG_FILE_NAME):
    os.remove(LOG_FILE_NAME)
    print("Log file removed")

# Setting up Yagmail
password = ""
with open("/home/shyana/.local/share/.email_password", "r") as f:
    password = f.read()
yag = yagmail.SMTP("photobooth263@gmail.com", password)

print("All configurations are done. Ready to capture photos!")

try:
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == GPIO.HIGH:
            flash_led(RED_LED_PIN, 3, 0.5)

            photo_files = []  # Store S3 URLs here

            for _ in range(3):  # Take 3 photos
                flash_led(BLUE_LED_PIN, 1, 0.5)
                time.sleep(2)
               
                # Capture photo
                photo_file_name = take_photo(camera)
                update_photo_log_file(photo_file_name)
                photo_files.append(photo_file_name)

                # Upload photo to S3
                s3_url = upload_to_s3(photo_file_name)

                print("📸 Photo captured & uploaded!")

            flash_led(RED_LED_PIN, 3, 0.5)

            # Send email with S3 links
            if photo_files:
                send_email_with_photo(yag, photo_files)
                print(" Email sent with S3 links!")
            else:
                print("No photos uploaded, so no email was sent.")

            print("Process complete! Press the button again for new photos.")

# Clean up GPIOs if a keyboard interrupt occurs
except KeyboardInterrupt:
    GPIO.cleanup()