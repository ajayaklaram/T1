import cv2
import os
import numpy as np
import torch
from facenet_pytorch import MTCNN

# Input and output paths
input_video_path = r'C:\Users\Ajaya\Downloads\WhatsApp_Video_2024_11_04_at_10_52_03_56c8d63d_V1.mp4'
output_folder_path = r'C:\Users\Ajaya\OneDrive\Documents\Desktop\detecteVideo'

# Create the output folder if it doesn't exist
os.makedirs(output_folder_path, exist_ok=True)

# Load the video
cap = cv2.VideoCapture(input_video_path)

# Frame skip value to speed up processing
frame_skip = 5  # Change this to adjust how many frames are skipped

# Initialize the MTCNN face detection model
mtcnn = MTCNN(keep_all=True, device='cuda' if torch.cuda.is_available() else 'cpu')

try:
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Check if the frame is valid
        if frame is None or not isinstance(frame, np.ndarray):
            continue

        # Skip frames to speed up processing
        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        boxes, _ = mtcnn.detect(rgb_frame)

        # If faces are detected, save them as images
        if boxes is not None:
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = [int(coord) for coord in box]

                # Ensure coordinates are within frame boundaries
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(frame.shape[1], x2), min(frame.shape[0], y2)

                # Extract the face from the frame
                face = frame[y1:y2, x1:x2]

                # Save the detected face
                face_filename = os.path.join(output_folder_path, f'face_frame{frame_count}_face{i}.jpg')
                cv2.imwrite(face_filename, face)

        print(f"Processing frame {frame_count}...")
        frame_count += 1
except KeyboardInterrupt:
    print("Processing interrupted by user.")
finally:
    # Release the video capture object
    cap.release()
    print("Video capture released.")

print("Face detection completed and saved in output folder.")
