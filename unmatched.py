import os
import cv2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import time
from PIL import Image
from deepface import DeepFace
import numpy as np

# Load Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'C:\Users\Ajaya\Downloads\vertical-sunset-440402-h4-f3e25263f3a1.json'

# Check if the service account file exists
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    print(f"Service account file not found at {SERVICE_ACCOUNT_FILE}")
    drive_service = None
else:
    try:
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)
        print("Google Drive service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Google Drive service: {e}")
        drive_service = None

# Folder IDs
aadhar_folder_id = '1Qtb5DYzSFE67Mbb5ZgDIqWUtdJaDD2F4'
cphotos_folder_id = '1DGeRqRbCPcfLDdEgP0h5fyX-MF8EQ8AH'
suspects_folder_id = '1N3RMhVD0OygeufLPYod6IYLtqzvlm3Jv'

def list_files_in_folder(folder_id):
    """Lists files in the specified Google Drive folder."""
    if drive_service is None:
        print("Drive service is not initialized. Cannot list files.")
        return []

    print(f"Listing files in folder ID: {folder_id}")
    query = f"'{folder_id}' in parents and trashed=false"
    try:
        results = drive_service.files().list(q=query, pageSize=1000, fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"Found {len(files)} files in folder ID: {folder_id}.")
        return files
    except Exception as e:
        print(f"Error listing files in folder ID: {folder_id} - {e}")
        return []

def download_file(file_id, file_name):
    """Downloads a file from Google Drive."""
    if drive_service is None:
        print("Drive service is not initialized. Cannot download files.")
        return None

    print(f"Attempting to download file: {file_name} (ID: {file_id})")
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        with open(file_name, 'wb') as f:
            f.write(file_io.getvalue())
        print(f"Successfully downloaded file: {file_name}")
        return file_name
    except Exception as e:
        print(f"Error downloading file ID: {file_id} - {e}")
        return None

def verify_and_fix_image(image_path):
    """Verifies and cleans up an image file."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            img.save(image_path)
        print(f"Image verified and cleaned: {image_path}")
        return True
    except Exception as e:
        print(f"Image verification failed for {image_path}. Error: {e}")
        return False

def upload_file(file_path, folder_id):
    """Uploads a file to Google Drive."""
    if drive_service is None:
        print("Drive service is not initialized. Cannot upload files.")
        return None

    print(f"Uploading file: {file_path} to folder ID: {folder_id}")
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    try:
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Uploaded file ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        print(f"Error uploading file {file_path} to folder ID: {folder_id} - {e}")
        return None

def detect_faces_deepface(image_path):
    """Detects and analyzes faces in an image using DeepFace."""
    print(f"Detecting faces in image: {image_path} using DeepFace")
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        print(f"DeepFace analysis result: {result}")
        return result
    except Exception as e:
        print(f"Error detecting faces with DeepFace: {e}")
        return None

def compare_faces_deepface(img1_path, img2_path):
    """Compares two images using DeepFace with ArcFace model."""
    try:
        result = DeepFace.verify(img1_path=img1_path, img2_path=img2_path, model_name='ArcFace', enforce_detection=False)
        return result['verified']
    except Exception as e:
        print(f"Error comparing faces using DeepFace: {e}")
        return False

def process_images(aadhar_folder_id, cphotos_folder_id, suspects_folder_id):
    """Processes images for face detection and comparison."""
    if drive_service is None:
        print("Drive service is not initialized. Exiting process.")
        return

    print("Starting processing of images...")
    aadhar_files = list_files_in_folder(aadhar_folder_id)
    cphotos_files = list_files_in_folder(cphotos_folder_id)

    aadhar_images = []
    for file in aadhar_files:
        print(f"Processing Aadhar file: {file['name']}")
        file_path = download_file(file['id'], file['name'])
        if file_path and verify_and_fix_image(file_path):
            aadhar_images.append(file_path)

    for file in cphotos_files:
        print(f"Processing CCTV file: {file['name']}")
        file_path = download_file(file['id'], file['name'])
        if not file_path or not verify_and_fix_image(file_path):
            continue

        matched = False
        for aadhar_image_path in aadhar_images:
            if compare_faces_deepface(aadhar_image_path, file_path):
                matched = True
                print(f"Match found for CCTV file: {file['name']} with Aadhar file: {os.path.basename(aadhar_image_path)}")
                break

        if not matched:
            upload_file(file_path, suspects_folder_id)
            print(f"Unmatched image uploaded: {file['name']}")
    print("Processing of images completed.")

def main():
    """Main function to execute the image processing pipeline."""
    start_time = time.time()
    print("Script started...")
    process_images(aadhar_folder_id, cphotos_folder_id, suspects_folder_id)
    end_time = time.time()
    print(f"Script completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
