import cv2
import numpy as np
import requests

class CameraModule:
    def __init__(self, source):
        """
        Initialize with either a local camera index (e.g., 0) or an IP webcam URL.
        """
        self.is_ip_camera = isinstance(source, str)
        if self.is_ip_camera:
            self.base_url = source
            self.video_url = f"{self.base_url}/video"
            self.image_url = f"{self.base_url}/shot.jpg"
        else:
            self.camera_index = source  # e.g., 0 for built-in camera

    def get_image(self):
        """
        Get a single frame from the source.
        """
        if self.is_ip_camera:
            try:
                response = requests.get(self.image_url, stream=True)
                response.raise_for_status()
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                return image
            except requests.RequestException as e:
                print(f"Error fetching image: {e}")
                return None
        else:
            cap = cv2.VideoCapture(self.camera_index)
            ret, frame = cap.read()
            cap.release()
            if ret:
                return frame
            else:
                print("Error capturing image from local webcam.")
                return None

    def stream_video(self):
        """
        Stream video from either local or IP camera.
        """
        source = self.video_url if self.is_ip_camera else self.camera_index
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame.")
                break

            cv2.imshow("Live Video Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
