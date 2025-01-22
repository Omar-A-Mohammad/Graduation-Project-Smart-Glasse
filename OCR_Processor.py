import cv2
import pytesseract
import json
import os
import time

class OCRProcessor:
    def __init__(self, tesseract_path:str="tesseract"):
        """
        Initialize the OCRProcessor with an optional path to Tesseract OCR executable.
        """
        if tesseract_path:
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                print(f"Warning: Tesseract path '{tesseract_path}' is invalid.")
                pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/Tesseract.exe'  # Default fallback

    def perform_ocr(self, image, conf_threshold:int=60):
        """
        Perform OCR on the given image and annotate it with bounding boxes and recognized text.
        
        Args:
            image_path (str): Path to the image file.
            conf_threshold (int): Minimum confidence level to consider text valid.

        Returns:
            str: JSON string containing recognized text and bounding box coordinates.
        """

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding, uncomment therholding method to use
        # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY) # Simple Threholding
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2) # Gaussian adaptive thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # Otsu's threholding

        # Perform OCR
        try:
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        except Exception as e:
            raise RuntimeError(f"Error occurred during OCR processing: {e}")

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

    def ocr_on_image(self, image_path, conf_threshold:int=60):
        """
        Perform OCR on the given image and annotate it with bounding boxes and recognized text.
        
        Args:
            image_path (str): Path to the image file.
            conf_threshold (int): Minimum confidence level to consider text valid.

        Returns:
            str: JSON string containing recognized text and bounding box coordinates.
        """
        # Check if image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"The image file '{image_path}' does not exist.")

        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read the image '{image_path}'. Ensure it's a valid image file.")

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding, uncomment therholding method to use
        # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY) # Simple Threholding
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2) # Gaussian adaptive thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # Otsu's threholding

        # Perform OCR
        try:
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        except Exception as e:
            raise RuntimeError(f"Error occurred during OCR processing: {e}")

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

    def display_annotated_image(self, window_name: str = "OCR Results"):
        """
        Display the annotated image with bounding boxes and text.

        Args:
            window_name (str): Name of the display window.
        """
        if hasattr(self, 'annotated_image'):
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.imshow(window_name, self.annotated_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("No annotated image available. Perform OCR first.")

    def save_annotated_image(self, output_path: str):
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


    def demo(self, image_filepath: str):
        """
        Perform a sample OCR operation for demonstration purposes.

        Args:
            image_filepath (str): Path to the image on which we'll perform OCR
        
        """

        # Initialize the OCR processor with the Tesseract path (example)
        self.tesseract_path='C:/Program Files/Tesseract-OCR/Tesseract.exe'
        
        # Record the start time
        start_time = time.time()
        
        try:
            # Perform OCR
            image_path = image_filepath  # Replace with your image path
            json_results = self.ocr_on_image(image_path)
            
            # Record the end time
            end_time = time.time()
            
            # Calculate and display the runtime
            runtime = end_time - start_time
            print(f"OCR process completed in {runtime:.2f} seconds")
            
            # Print the JSON results
            print("Recognized Text and Locations:")
            print(json_results)
            
            # Display and save the annotated image
            self.display_annotated_image()
            self.save_annotated_image("annotated_image.jpg")
            
        except Exception as e:
            print(f"An error occurred: {e}")