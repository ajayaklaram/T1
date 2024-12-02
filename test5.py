import os
import cv2
import shutil
from deepface import DeepFace
from retinaface import RetinaFace
import pdfplumber 



# Paths
aadhaar_folder = r'C:\Users\OM\Desktop\Facecomparison\aadharcard'
cctv_folder = r'C:\Users\OM\Desktop\Facecomparison\cctv'
aadhaar_faces_folder = r'C:\Users\OM\Desktop\Facecomparison\aadhaar_faces'
cctv_faces_folder = r'C:\Users\OM\Desktop\Facecomparison\cctv_faces'
matched_folder = r'C:\Users\OM\Desktop\Facecomparison\matched'
unmatched_folder = r'C:\Users\OM\Desktop\Facecomparison\unmatched'

# Create output directories if they don't exist
for folder in [aadhaar_faces_folder, cctv_faces_folder, matched_folder, unmatched_folder]:
    os.makedirs(folder, exist_ok=True)

# Camera constants based on Trueview 2MP specs
SENSOR_WIDTH_MM = 4.8
FOCAL_LENGTH_MM = 2.8
IMAGE_WIDTH_PX = 1920
KNOWN_FACE_WIDTH = 14  # Average human face width in cm
MAX_DISTANCE_CM = 500  # 5 meters

# Calculate focal length in pixels
FOCAL_LENGTH_PX = (IMAGE_WIDTH_PX * FOCAL_LENGTH_MM) / SENSOR_WIDTH_MM

# Helper functions
def calculate_distance(actual_width, focal_length, apparent_width):
    """Calculate distance based on focal length and apparent width of a face."""
    return (actual_width * focal_length) / apparent_width  # Distance in centimeters

def detect_faces_retina(image_path, output_folder, crop_margin=40):
    """
    Detect faces using RetinaFace and verify using size filters.
    """
    faces = RetinaFace.detect_faces(image_path)
    img = cv2.imread(image_path)

    if faces is None or len(faces) == 0:
        print(f"No faces detected in {image_path}.")
        return []

    extracted_faces = []
    for i, key in enumerate(faces.keys()):
        face_info = faces[key]["facial_area"]
        x1, y1, x2, y2 = face_info

        # Calculate face size
        face_width_px = x2 - x1
        distance_cm = calculate_distance(KNOWN_FACE_WIDTH, FOCAL_LENGTH_PX, face_width_px)

        # Ignore faces that are too far
        if distance_cm > MAX_DISTANCE_CM:
            print(f"Face detected in {image_path} | Distance: {distance_cm:.2f} cm | Status: IGNORED (too far)")
            continue
        else:
            print(f"Face detected in {image_path} | Distance: {distance_cm:.2f} cm | Status: ACCEPTED")

        # Add crop margin
        x1 = max(0, x1 - crop_margin)
        y1 = max(0, y1 - crop_margin)
        x2 = min(img.shape[1], x2 + crop_margin)
        y2 = min(img.shape[0], y2 + crop_margin)

        face = img[y1:y2, x1:x2]
        if face.size == 0:
            print(f"Empty face detected in {image_path}. Skipping.")
            continue

        face_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0]}_face_{i + 1}.jpg")
        cv2.imwrite(face_path, face)
        extracted_faces.append(face_path)
    return extracted_faces

def process_folder(input_folder, output_folder):
    """Processes images in a folder and extracts valid faces."""
    for img_file in os.listdir(input_folder):
        if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"Skipping non-image file: {img_file}")
            continue
        img_path = os.path.join(input_folder, img_file)
        detect_faces_retina(img_path, output_folder, crop_margin=40)

def compare_faces(aadhaar_faces_folder, cctv_faces_folder):
    """Compare faces using VGG-Face."""
    aadhaar_faces = [os.path.join(aadhaar_faces_folder, f) for f in os.listdir(aadhaar_faces_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    cctv_faces = [os.path.join(cctv_faces_folder, f) for f in os.listdir(cctv_faces_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for cctv_face in cctv_faces:
        matched = False  # Reset matched flag for each CCTV face
        for aadhaar_face in aadhaar_faces:
            try:
                # Use VGG-Face model for comparison
                result = DeepFace.verify(img1_path=cctv_face, img2_path=aadhaar_face, model_name="VGG-Face", enforce_detection=False)
                if result['verified']:
                    shutil.copy(cctv_face, os.path.join(matched_folder, os.path.basename(cctv_face)))
                    print(f"Matched: {os.path.basename(cctv_face)} with Aadhaar face: {os.path.basename(aadhaar_face)}")
                    matched = True
                    break
            except Exception as e:
                print(f"Error comparing {cctv_face} with {aadhaar_face}: {e}")

        if not matched:
            shutil.copy(cctv_face, os.path.join(unmatched_folder, os.path.basename(cctv_face)))
            print(f"Unmatched: {os.path.basename(cctv_face)}")

# Main processing
print("Extracting faces from Aadhaar folder...")
process_folder(aadhaar_folder, aadhaar_faces_folder)

print("Extracting faces from CCTV folder...")
process_folder(cctv_folder, cctv_faces_folder)

print("Comparing extracted faces...")
compare_faces(aadhaar_faces_folder, cctv_faces_folder)

print("Processing complete.")
