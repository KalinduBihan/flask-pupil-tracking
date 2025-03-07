import cv2
import os

def crop_frame(frame, crop_height=200, width=640, height=480):
    """Crop a fixed rectangle from the top border of the frame."""
    h, w, _ = frame.shape

    # Ensure crop height does not exceed the frame height
    if crop_height < h:
        # Crop the top `crop_height` pixels and keep the rest
        cropped = frame[crop_height:h, 0:w]
    else:
        print("Error: Crop dimensions exceed frame dimensions.")
        return None

    # Resize the cropped frame to match the desired output size (640x480)
    cropped_resized = cv2.resize(cropped, (width, height))

    return cropped_resized

def process_crop_video(video_path):
    """Process the video to crop out the top rectangle and resize the remaining part."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video.")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video resolution: {frame_width}x{frame_height}")

    # Define output video file
    output_path = os.path.splitext(video_path)[0] + "_cropped.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (640, 480))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Crop the frame (remove top part)
        cropped_frame = crop_frame(frame, crop_height=180)  # Crop top 200px (adjust as needed)

        if cropped_frame is not None:
            # Write the cropped frame to the output video
            out.write(cropped_frame)

            # Optional: Display the cropped frame while processing
            # cv2.imshow('Cropped Frame', cropped_frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Cropped video saved as: {output_path}")

# Example usage
# video_path = "C:/Users/kalin/Desktop/Device_mimic/videoori.webm"  # Change to your actual video path
# process_crop_video(video_path)
