# import libraries 
import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import os
import yagmail

# Pin configuration variables and paths
LOG_FILE_NAME = "/home/<home_directory>/camera/photo_logs.txt"
PIR_PIN = 4
LED_PIN = 17
BUTTON_PIN = 26

# function to capture a photo in corresponding directory and return file path
def take_photo(camera):
    file_name = "/home/<home_directory>/camera/img_" + str(time.time()) + ".jpg"
    camera.capture(file_name)
    return file_name

# function to update log file with file name of newly taken photo
def update_photo_log_file(photo_file_name):
    with open(LOG_FILE_NAME, "a") as f:
        f.write(photo_file_name)
        f.write("\n")

# function to send photo to client using yagmail
def send_email_with_photo(yagmail_client, file_name):
    yagmail_client.send(to='<enter personal email>',
         subject="A new photo has been taken!",
         contents="Thank you for working with us! We hope you enjoy your photos!",
         attachments=file_name)

# setting up camera 
camera = PiCamera()
camera.resolution = (720, 480)
camera.rotation = 180
print("Waiting 2 seconds to init the camera...")
time.sleep(2)
print("Camera has been setup")

# setting up GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.output(LED_PIN, GPIO.LOW)
print("GPIOs have been setup")

# variables
MOV_DETECT_THRESHOLD = 1.0
last_pir_state = GPIO.input(PIR_PIN)
movement_timer = time.time()
last_time_photo_taken = 0
MIN_DURATION_BETWEEN_TWO_PHOTOS = 5.0
program_started = 0

# removing log file if it already exists 
if os.path.exists(LOG_FILE_NAME):
    os.remove(LOG_FILE_NAME)
    print("log file removed")

# setting up yagmail 
password = ""
with open("/home/<home_directory>/.local/share/.email_password", "r") as f:
    password = f.read()    
yag = yagmail.SMTP('photobooth263@gmail.com', password)

print("done all configurations")

try:
    while True:
        
        # capturing state of push button
        button_state = int(GPIO.input(BUTTON_PIN))
        
        # setting flag to indicate that the button has been pushed
        if button_state == 1:
            program_started = 1
        
        # start of program 
        if program_started == 1:
            time.sleep(0.01)
            
            # capturing state of sensor 
            pir_state = GPIO.input(PIR_PIN)
            
            # flashing LED if movement has been detected
            if pir_state == GPIO.HIGH:
                GPIO.output(LED_PIN, GPIO.HIGH)
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
            
            # capturing time difference between movements being detected
            if last_pir_state == GPIO.LOW and pir_state == GPIO.HIGH:
                movement_timer = time.time()
            
            # if movement has been detected 
            if last_pir_state == GPIO.HIGH and pir_state == GPIO.HIGH:
                
                # if the time duration between movements detected meets threshold
                if time.time() - movement_timer > MOV_DETECT_THRESHOLD:
                    
                    # if the time duration between photos taken meets the threshold
                    if time.time() - last_time_photo_taken > MIN_DURATION_BETWEEN_TWO_PHOTOS:
                        
                        # take photo
                        photo_file_name = take_photo(camera)
                        print("Photo has been taken")
                        
                        # update photo log
                        update_photo_log_file(photo_file_name)
                        
                        # email client with photo
                        send_email_with_photo(yag, photo_file_name)
                        
                        # update timer since last photo taken 
                        last_time_photo_taken = time.time()
            
            # update sensor state
            last_pir_state = pir_state

# clean up GPIOs if keyboard interrupt has occurred            
except KeyboardInterrupt:
    GPIO.cleanup()

