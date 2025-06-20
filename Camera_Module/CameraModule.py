import cv2
import requests
import numpy as np

class CameraModule:
    def __init__(self, source):
        """
        Initialize the CameraModule with either a camera index (int) or an IPWebcam URL (str).
        :param source: Camera index (e.g., 0) or base URL of the IPWebcam server (e.g., http://192.168.xxx.xxx:8080)
        """
        if isinstance(source, int):
            # Use built-in webcam
            self.is_ip_camera = False
            self.cap = cv2.VideoCapture(source)
        else:
            # Use IP webcam
            self.is_ip_camera = True
            self.base_url = source
            self.video_url = f"{self.base_url}/video"
            self.image_url = f"{self.base_url}/shot.jpg"

    def get_image(self):
        """
        Get a single frame from the camera.
        :return: Frame as numpy array or None if failed.
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
            if not self.cap.isOpened():
                print("Error: Cannot access laptop camera.")
                return None
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                print("Error: Failed to capture frame from laptop camera.")
                return None

    def stream_video(self):
        """
        Stream live video from the camera.
        Press 'q' to quit the stream.
        """
        if self.is_ip_camera:
            cap = cv2.VideoCapture(self.video_url)
        else:
            cap = self.cap

        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame from video stream.")
                break

            cv2.imshow("Live Video Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
