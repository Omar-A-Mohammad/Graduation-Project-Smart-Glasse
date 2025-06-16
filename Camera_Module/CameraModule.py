import cv2
import requests
import numpy as np

class CameraModule:
    def __init__(self, base_url):
        """
        Initialize the CameraModule with the base URL of the IPWebcam server.
        :param base_url: Base URL of the IPWebcam server (e.g., http://192.168.xxx.xxx:8080)
        """
        self.base_url = base_url
        self.video_url = f"{self.base_url}/video"
        self.image_url = f"{self.base_url}/shot.jpg"

    def get_image(self):
        """
        Fetch a single image from the IPWebcam server.
        :return: The image as a numpy array (OpenCV format) or None if the request fails.
        """
        try:
            response = requests.get(self.image_url, stream=True)
            response.raise_for_status()
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except requests.RequestException as e:
            print(f"Error fetching image: {e}")
            return None

    def stream_video(self):
        """
        Stream live video feed from the IPWebcam server.
        Press 'q' to exit the video stream.
        """
        cap = cv2.VideoCapture(self.video_url)
        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame from video stream.")
                break

            cv2.imshow("Live Video Feed", frame)

            # Exit the video stream when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    camera = CameraModule("http://192.168.100.7:8080")

    # Fetch and display a single image
    image = camera.get_image()
    if image is not None:
        cv2.imshow("Single Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Stream live video feed
    camera.stream_video()