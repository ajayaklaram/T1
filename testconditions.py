import os
import cv2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from deepface import DeepFace
from PIL import Image
from simple_salesforce import Salesforce
import io

# Disable TensorFlow oneDNN optimization warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'C:\Users\Ajaya\Downloads\vertical-sunset-440402-h4-f3e25263f3a1.json'

# Salesforce credentials
SF_USERNAME = 'navyagrand7890@gmail.com'
SF_PASSWORD = 'navya@123'
SF_SECURITY_TOKEN = 'NeAPhh5Puxmc1EsL1IJPcQB5'

# Initialize Google Drive service
try:
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)
    print("Google Drive service initialized successfully.")
except Exception as e:
    print(f"Error initializing Google Drive service: {e}")
    drive_service = None

# Initialize Salesforce connection
try:
    sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token=SF_SECURITY_TOKEN)
    print("Salesforce service initialized successfully.")
except Exception as e:
    print(f"Error initializing Salesforce service: {e}")
    sf = None

# Folder IDs
aadhar_folder_id = '1Qtb5DYzSFE67Mbb5ZgDIqWUtdJaDD2F4'
cphotos_folder_id = '1DGeRqRbCPcfLDdEgP0h5fyX-MF8EQ8AH'
suspects_folder_id = '1N3RMhVD0OygeufLPYod6IYLtqzvlm3Jv'

# Helper Functions
def list_files_in_folder(folder_id):
    """Lists files in the specified Google Drive folder."""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, pageSize=1000, fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error listing files in folder ID: {folder_id} - {e}")
        return []

def download_file(file_id, file_name):
    """Downloads a file from Google Drive."""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        download_path = os.path.join("downloads", file_name)
        os.makedirs("downloads", exist_ok=True)
        with open(download_path, 'wb') as f:
            f.write(file_io.getvalue())
        return download_path
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
        return True
    except Exception:
        return False

def upload_file(file_path, folder_id):
    """Uploads a file to Google Drive."""
    try:
        file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file.get('id'), file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading file: {file_path} - {e}")
        return None, None

def detect_and_split_faces(image_path):
    """Detects and splits multiple faces in an image."""
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        face_images = []
        for idx, (x, y, w, h) in enumerate(faces):
            face_img = img[y:y + h, x:x + w]
            face_filename = f"downloads/cropped_face_{os.path.basename(image_path)}_{idx}.jpg"
            cv2.imwrite(face_filename, face_img)
            face_images.append(face_filename)
        return face_images
    except Exception as e:
        print(f"Error during face detection and splitting: {e}")
        return []

def compare_faces_deepface(img1_path, face_img_path):
    """Compares two images using DeepFace."""
    try:
        result = DeepFace.verify(img1_path=img1_path, img2_path=face_img_path, model_name='ArcFace', enforce_detection=False)
        return result['verified']
    except Exception as e:
        print(f"Error comparing faces using DeepFace: {e}")
        return False

def create_suspect_record_in_salesforce(file_id, file_name, file_url):
    """Creates a record in Salesforce for unmatched faces."""
    try:
        record = {
            'Name': file_name,
            'File_ID__c': file_id,
            'File_Name__c': file_name,
            'File_URL__c': file_url
        }
        sf.zia__c.create(record)
    except Exception as e:
        print(f"Error creating Salesforce record: {e}")

# Main Process
def process_images_with_multiple_faces(aadhar_folder_id, cphotos_folder_id, suspects_folder_id):
    """Processes images for face detection, splitting, and comparison."""
    aadhar_files = list_files_in_folder(aadhar_folder_id)
    cphotos_files = list_files_in_folder(cphotos_folder_id)

    aadhar_images = []
    for file in aadhar_files:
        file_path = download_file(file['id'], file['name'])
        if file_path and verify_and_fix_image(file_path):
            aadhar_images.append(file_path)

    for file in cphotos_files:
        file_path = download_file(file['id'], file['name'])
        if not file_path or not verify_and_fix_image(file_path):
            continue

        face_images = detect_and_split_faces(file_path)
        if not face_images:
            continue

        for face_image_path in face_images:
            matched = any(compare_faces_deepface(aadhar_image, face_image_path) for aadhar_image in aadhar_images)
            if not matched:
                uploaded_file_id, uploaded_file_url = upload_file(face_image_path, suspects_folder_id)
                if uploaded_file_id:
                    create_suspect_record_in_salesforce(uploaded_file_id, os.path.basename(face_image_path), uploaded_file_url)

# Main Function
def main():
    """Main function to initiate the face detection and comparison process."""
    try:
        # Check if Google Drive service and Salesforce connection are initialized
        if not drive_service:
            print("Error: Google Drive service is not initialized. Exiting.")
            return
        if not sf:
            print("Error: Salesforce service is not initialized. Exiting.")
            return

        # Start processing images
        print("Starting the process of face detection and comparison...")
        process_images_with_multiple_faces(aadhar_folder_id, cphotos_folder_id, suspects_folder_id)
        print("Process completed successfully.")

    except Exception as e:
        print(f"An error occurred in the main function: {e}")

# Execute
if __name__ == "__main__":
    main()
