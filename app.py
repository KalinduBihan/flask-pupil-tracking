from flask import Flask, request, jsonify
from flask_cors import CORS
from OrloskyPupilDetector_RealTime import process_video
from google.cloud import storage
from CameraCapture import process_crop_video
import os
import math

app = Flask(__name__)
CORS(app)

# Initialize Google Cloud Storage
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/kalin/Desktop/Cloud storage/biometricgaze-7f3cf41d6ef8.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/kalindubihanfdo/biometricgaze-7f3cf41d6ef8.json"

client = storage.Client()
print("Connected to Google Cloud Storage. Project ID:", client.project)

bucket_name = 'eye-tracker-videos-12345'

try:
    bucket = client.get_bucket(bucket_name)
    print(f"Successfully connected to {bucket_name}")
except Exception as e:
    print(f"Error: {e}")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400  

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_file_path)

        cropped_video_path = os.path.splitext(temp_file_path)[0] + "_cropped.mp4"
        process_crop_video(temp_file_path)

        if not os.path.exists(cropped_video_path):
            return jsonify({'error': 'Video processing failed'}), 500

        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(os.path.basename(cropped_video_path))
        blob.upload_from_filename(cropped_video_path)

        os.remove(temp_file_path)
        os.remove(cropped_video_path)

        return jsonify({'message': 'Cropped video uploaded successfully'}), 200

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/eyeCoordinates', methods=['POST'])
def get_eye_coordinates():
    try:
        data = request.get_json()
        if not data or 'video_path' not in data:
            return jsonify({"error": "Missing video_path in request body"}), 400

        video_gcs_path = data['video_path']
        video_filename = os.path.basename(video_gcs_path)
        local_video_path = os.path.join(UPLOAD_FOLDER, video_filename)

        # Download the video from Google Cloud Storage
        blob = bucket.blob(video_filename)
        blob.download_to_filename(local_video_path)

        # Process video for eye tracking
        eye_coordinates = process_video(local_video_path, 1)

        # Calculate focus index
        focus_index = calculate_focus_index(eye_coordinates)

        print("Focus index: " + str(focus_index))

        os.remove(local_video_path)

        return jsonify({"eye_coordinates": eye_coordinates, "focus_index": focus_index}), 200

    except Exception as e:
        print(f"Error processing eye coordinates: {e}")
        return jsonify({"error": str(e)}), 500

def calculate_focus_index(pupil_movements, reference_point=(370.10, 170.09), threshold=76):
    eye_contacts = 0
    total_seconds = len(pupil_movements)

    for movement in pupil_movements:
        x, y = movement.get('x'), movement.get('y')
        
        # Skip this movement if x or y is None
        if x is None or y is None:
            continue
        
        distance = math.sqrt((x - reference_point[0]) ** 2 + (y - reference_point[1]) ** 2)
        
        if distance <= threshold:
            eye_contacts += 1
    
    focus_index = (eye_contacts / total_seconds) * 100 if total_seconds > 0 else 0
    return round(focus_index, 2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)












# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from OrloskyPupilDetector_RealTime import process_video
# from google.cloud import storage
# from CameraCapture import process_crop_video
# import os
# import math

# app = Flask(__name__)
# CORS(app)

# # Initialize Google Cloud Storage
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/kalin/Desktop/Cloud storage/biometricgaze-7f3cf41d6ef8.json"

# client = storage.Client()
# print("Connected to Google Cloud Storage. Project ID:", client.project)

# bucket_name = 'eye-tracker-videos-12345'

# try:
#     bucket = client.get_bucket(bucket_name)
#     print(f"Successfully connected to {bucket_name}")
# except Exception as e:
#     print(f"Error: {e}")

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
# @app.route('/upload', methods=['POST'])
# def upload_video():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400  

#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'}), 400

#         temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#         file.save(temp_file_path)

#         cropped_video_path = os.path.splitext(temp_file_path)[0] + "_cropped.mp4"
#         process_crop_video(temp_file_path)

#         if not os.path.exists(cropped_video_path):
#             return jsonify({'error': 'Video processing failed'}), 500

#         bucket = client.get_bucket(bucket_name)
#         blob = bucket.blob(os.path.basename(cropped_video_path))
#         blob.upload_from_filename(cropped_video_path)

#         os.remove(temp_file_path)
#         os.remove(cropped_video_path)

#         return jsonify({'message': 'Cropped video uploaded successfully'}), 200

#     except Exception as e:
#         print(f"Upload error: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/eyeCoordinates', methods=['POST'])
# def get_eye_coordinates():
#     try:
#         data = request.get_json()
#         if not data or 'video_path' not in data:
#             return jsonify({"error": "Missing video_path in request body"}), 400

#         video_gcs_path = data['video_path']
#         video_filename = os.path.basename(video_gcs_path)
#         local_video_path = os.path.join(UPLOAD_FOLDER, video_filename)

#         # Download the video from Google Cloud Storage
#         blob = bucket.blob(video_filename)
#         blob.download_to_filename(local_video_path)

#         # Process video for eye tracking
#         eye_coordinates = process_video(local_video_path, 1)

#         # Clean up local copy
#         os.remove(local_video_path)

#         return jsonify(eye_coordinates), 200

#     except Exception as e:
#         print(f"Error processing eye coordinates: {e}")
#         return jsonify({"error": str(e)}), 500
    
#     import math

# def calculate_focus_index(pupil_movements, reference_point=(370.10, 170.09), threshold=76):
#     eye_contacts = 0
#     total_seconds = len(pupil_movements)
    
#     for movement in pupil_movements:
#         x, y = movement['x'], movement['y']
#         distance = math.sqrt((x - reference_point[0]) ** 2 + (y - reference_point[1]) ** 2)
        
#         if distance <= threshold:
#             eye_contacts += 1
    
#     focus_index = (eye_contacts / total_seconds) * 100 if total_seconds > 0 else 0
#     return round(focus_index, 2)

# # @app.route('/eyeCoordinates', methods=['POST'])
# # def get_eye_coordinates():
# #     data = request.get_json()
# #     if not data or 'video_path' not in data:
# #         return jsonify({"error": "Missing video_path in request body"}), 400
    
# #     video_path = data['video_path']
# #     eye_coordinates = process_video(video_path, 1) 
# #     return jsonify(eye_coordinates)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
