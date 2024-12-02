import cv2
import mediapipe as mp
import os
import numpy as np

# Input and output paths
input_video_path = r'C:\Users\Ajaya\Downloads\WhatsApp_Video_2024_11_04_at_10_52_03_56c8d63d_V1.mp4'
output_folder_path = r'C:\Users\Ajaya\OneDrive\Documents\Desktop\detecteVideo'

# Create the output folder if it doesn't exist
os.makedirs(output_folder_path, exist_ok=True)

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Load the video
cap = cv2.VideoCapture(input_video_path)

# Frame skip value to speed up processing
frame_skip = 5  # Change this to adjust how many frames are skipped

# Initialize face detection model
try:
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
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

            # Process the frame for face detection
            results = face_detection.process(rgb_frame)

            # If faces are detected, save them as images
            if results.detections:
                for i, detection in enumerate(results.detections):
                    # Get the bounding box of the face
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                    # Extract the face from the frame
                    face = frame[y:y + h, x:x + w]

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
