import boto3
import os

# AWS S3 Configuration
S3_BUCKET = "ss-photobooth-uploads"  # 🔹 Replace with your actual bucket name
S3_REGION = "us-east-2"  # 🔹 Replace with your AWS region

# Initialize S3 Client
s3 = boto3.client("s3")

def upload_to_s3(file_path, s3_filename):
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_filename)
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_filename}"
        print(f"Upload successful: {file_url}")
        return file_url
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

# 🔹 Replace with a test image file from your Raspberry Pi
test_image = "/home/shyana/camera/img_1725938207.3745759.jpg"  # Update path if needed
s3_destination = f"uploads/{os.path.basename(test_image)}"

upload_to_s3(test_image, s3_destination)