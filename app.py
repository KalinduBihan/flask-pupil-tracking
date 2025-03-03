from flask import Flask, request, jsonify
from OrloskyPupilDetector_RealTime import process_video

app = Flask(__name__)

@app.route('/eyeCoordinates', methods=['POST'])
def get_eye_coordinates():
    data = request.get_json()
    if not data or 'video_path' not in data:
        return jsonify({"error": "Missing video_path in request body"}), 400
    
    video_path = data['video_path']
    eye_coordinates = process_video(video_path, 1) 
    return jsonify(eye_coordinates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# from flask import Flask, request, jsonify, Response, render_template
# from flask_cors import CORS
# from OrloskyPupilDetector_RealTime import process_video_realtime, start_logging, stop_logging, generate_video_feed
# import threading

# app = Flask(__name__)
# CORS(app)

# camera_started = False

# def start_camera_process():
#     global camera_started
#     if not camera_started:
#         thread = threading.Thread(target=process_video_realtime, daemon=True)
#         thread.start()
#         camera_started = True

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/startCam', methods=['GET'])
# def start_camera():
#     start_camera_process()
#     return jsonify({"message": "Camera started successfully"})

# @app.route('/startLoggingCam', methods=['POST'])
# def start_logging_endpoint():
#     if not camera_started:
#         return jsonify({"error": "Camera is not started"}), 400
    
#     response = start_logging()
#     return response

# @app.route('/stopLoggingCam', methods=['GET'])
# def stop_logging_endpoint():
#     if not camera_started:
#         return jsonify({"error": "Camera is not started"}), 400
    
#     response = stop_logging()
#     return jsonify({"message": response})

# # @app.route('/video_feed')
# # def video_feed():
# #     """Video streaming route with continuous feed."""
# #     if not camera_started:
# #         return jsonify({"error": "Camera is not started"}), 400
    
# #     return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
