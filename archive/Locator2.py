import cv2
import pytesseract
import json

class OCRProcessor:
    def __init__(self, tesseract_path=None):
        """
        Initialize the OCRProcessor with an optional path to Tesseract OCR executable.
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def perform_ocr(self, image_path, conf_threshold=60):
        """
        Perform OCR on the given image and annotate it with bounding boxes and recognized text.
        
        Args:
            image_path (str): Path to the image file.
            conf_threshold (int): Minimum confidence level to consider text valid.

        Returns:
            str: JSON string containing recognized text and bounding box coordinates.
        """
        # Load the image
        image = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Optional: Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Perform OCR
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        results = []

        # Process detected text
        for i in range(len(data['text'])):
            text = data['text'][i].strip()  # Remove leading and trailing spaces
            if int(data['conf'][i]) > conf_threshold and text:  # Ignore empty or low-confidence text
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                # Store the text and its bounding box
                results.append({
                    'text': text,
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h}
                })

                # Annotate the image
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Save the annotated image for later use
        self.annotated_image = image

        # Return results as a JSON string
        return json.dumps(results, indent=4)

    def display_annotated_image(self, window_name="OCR Results"):
        """
        Display the annotated image with bounding boxes and text.

        Args:
            window_name (str): Name of the display window.
        """
        if hasattr(self, 'annotated_image'):
            cv2.imshow(window_name, self.annotated_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("No annotated image available. Perform OCR first.")

    def save_annotated_image(self, output_path):
        """
        Save the annotated image to the specified path.

        Args:
            output_path (str): Path to save the annotated image.
        """
        if hasattr(self, 'annotated_image'):
            cv2.imwrite(output_path, self.annotated_image)
            print(f"Annotated image saved to {output_path}")
        else:
            print("No annotated image available. Perform OCR first.")


# Example Usage

import time

if __name__ == "__main__":
    # Initialize the OCR processor with the Tesseract path (if required)
    ocr = OCRProcessor(tesseract_path='C:/Program Files/Tesseract-OCR/Tesseract.exe')
    
    # Record the start time
    start_time = time.time()
    
    # Perform OCR
    image_path = "sample.jpg"  # Replace with your image path
    json_results = ocr.perform_ocr(image_path)
    
    # Record the end time
    end_time = time.time()
    
    # Calculate and display the runtime
    runtime = end_time - start_time
    print(f"OCR process completed in {runtime:.2f} seconds")
    
    # Print the JSON results
    print("Recognized Text and Locations:")
    print(json_results)
    
    # Display and save the annotated image
    ocr.display_annotated_image()
    ocr.save_annotated_image("annotated_image.jpg")
