from ultralytics import YOLO
import json

class YOLODetector:
    def __init__(self, model_path):
        """
        Initialize the YOLO detector with the model path.
        :param model_path: Path to the YOLO model weights (e.g., 'best.pt').
        """
        self.model = YOLO(model_path)

    def run_inference(self, image_path):
        """
        Run inference on the given image.
        :param image_path: Path to the input image.
        :return: Inference results.
        """
        self.results = self.model(image_path)
        return self.results

    def process_results(self, normalize=False):
        """
        Process the inference results and extract detections.
        :param normalize: If True, normalize bounding box coordinates to [0, 1].
        :return: List of detections with class names, bounding boxes, and confidence scores.
        """
        detections = []

        for result in self.results:
            image_width, image_height = result.orig_shape[1], result.orig_shape[0]  # Get image dimensions

            for box in result.boxes:
                # Extract bounding box coordinates
                x_center = float(box.xywh[0][0])
                y_center = float(box.xywh[0][1])
                width = float(box.xywh[0][2])
                height = float(box.xywh[0][3])

                # Normalize coordinates if requested
                if normalize:
                    x_center /= image_width
                    y_center /= image_height
                    width /= image_width
                    height /= image_height

                # Extract class and confidence
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])  # Confidence score

                # Append detection to the list
                detections.append({
                    "text": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x": x_center,
                        "y": y_center,
                        "width": width,
                        "height": height
                    }
                })

        return detections

    def save_results(self, detections, output_path):
        """
        Save the detections to a JSON file.
        :param detections: List of detections.
        :param output_path: Path to save the JSON file.
        """
        with open(output_path, "w") as f:
            json.dump(detections, f, indent=4)

    def load_results(self, json_path):
        """
        Load detections from a JSON file.
        :param json_path: Path to the JSON file.
        :return: Loaded detections.
        """
        with open(json_path) as f:
            return json.load(f)


# Example usage
if __name__ == "__main__":
    # Initialize the detector
    detector = YOLODetector("Currency_Module/cur_n100_runs/best.pt")

    # Run inference on an image
    results = detector.run_inference("Currency_Module/001456598.jpg")

    # Process the results (normalize bounding boxes)
    detections = detector.process_results(normalize=False)

    # Save the results to a JSON file
    detector.save_results(detections, "output_2.json")

    # Load and print the results
    loaded_detections = detector.load_results("output_2.json")
    print(loaded_detections)