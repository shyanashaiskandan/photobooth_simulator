# import libraries 
from flask import Flask
import os

# initializing file paths and variables
CAMERA_FOLDER_PATH = "/home/shyana/camera"
LOG_FILE_NAME = CAMERA_FOLDER_PATH + "/photo_logs.txt"
photo_counter = 0

# initalizing Flask web app
app = Flask(__name__, static_url_path=CAMERA_FOLDER_PATH, static_folder = CAMERA_FOLDER_PATH)

# creating home route
@app.route("/")
def index():
    return "Home Page"

# creating photo gallery route
@app.route("/photo-gallery")
def check_movement():
    message = ""
    line_counter = 0
    last_photo_file_name = ""
    
    # if new photos exists
    if os.path.exists(LOG_FILE_NAME):
        
        # update value of new photos taken since last checked in line_counter
        with open (LOG_FILE_NAME, "r") as f:
            for line in f:
                line_counter += 1
                last_photo_file_name = line
        global photo_counter
        
        # find number of new photos taken since last checked and update web page
        difference = line_counter - photo_counter
        message = str(difference) + " photos were taken since you last checked <br></br>"
        
        # include the file path of the last photo taken 
        message += "Last photo: " + last_photo_file_name + "<br/>"
        
        # include the last photo taken 
        message += "<img src=\"" + last_photo_file_name + "\">"
        photo_counter = line_counter
    else:
        
        # default message if no new photos have been taken 
        message = "nothing new"
    return message
    
# run app with configured host
app.run(host="0.0.0.0")