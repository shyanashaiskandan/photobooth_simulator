# 📸 Photo Booth Simulator

A Django-based web application that simulates a photo booth experience, allowing users to capture photos and receive them via email. Built to run seamlessly on Raspberry Pi hardware with camera, sensors, and visual indicators.

---

## ⚙️ Setup

1. Install Dependencies:
   ```bash
   pip install django boto3 yagmail picamera RPi.GPIO Pillow
   ```

2. Navigate to the Django Project Directory:
   ```bash
   cd photobooth_project
   ```

3. Apply Django Migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the Django Development Server:
   ```bash
   python manage.py runserver
   ```
   - The app will be available at `http://127.0.0.1:8000/` by default.

---

## ✨ Features

- Built with Django’s backend framework  
- Capture photos using a Raspberry Pi camera  
- Upload photos to AWS S3 using boto3  
- Send photos via email using yagmail  
- Motion sensor triggers camera activation when user presence is detected  
- Three red flashing lights signal the start and end of the photo session  

---

## 🎮 Usage

1. Start the Django web app and open the photo booth interface  
2. When someone steps in front of the booth, the motion sensor automatically activates the system  
3. Click "Start Photobooth" to begin the session  
4. Three red lights will flash to signal the start of the photo capture process  
5. A blue light will flash each time a photo is taken  
6. After three photos are captured, the red lights will flash again to indicate the end of the session  
7. The photos are uploaded to the local webserver for viewing and saved to an AWS S3 bucket  
8. Enter your email address to receive direct links to your photos from the S3 bucket  
9. Click "Done" to finish and return to the home screen  

---

## 📝 Notes

- This project is designed to work with Raspberry Pi hardware. Make sure your Pi camera, LEDs, and motion sensor are properly connected and configured
  
---
