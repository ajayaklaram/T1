import cv2
import mtcnn
import os

# Path to your CCTV footage
video_path = r"C:\Users\Ajaya\Downloads\cctvvideo1.mp4"
output_folder = 'extracted_faces'

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize MTCNN detector
detector = mtcnn.MTCNN()

# Open the video file
cap = cv2.VideoCapture(video_path)

# Initialize frame count
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect faces in the frame
    faces = detector.detect_faces(frame)
    
    for face in faces:
        x, y, width, height = face['box']
        face_image = frame[y:y+height, x:x+width]
        cv2.imwrite(f'{output_folder}/face_{frame_count}.jpg', face_image)
    
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
