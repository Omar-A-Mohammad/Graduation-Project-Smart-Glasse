import cv2
import pytesseract

class TextExtractor:

    def __init__(self, image: str):
        self.image = image
        self.text_with_locations = []  # List to store text with bounding box info
        self.fullText = ""

    def __str__(self):
        return "The TextExtractor class processes images to extract text and bounding box locations using PyTesseract."

    def set_tesseract_cmd(self, path: str):
        pytesseract.pytesseract.tesseract_cmd = path

    def extract_text(self):
        # Read and preprocess the image
        img = cv2.imread(self.image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Dilation to merge text regions
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

        # Finding contours
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Initialize results
        self.text_with_locations = []
        self.fullText = ""

        # Loop through contours to extract text and bounding box locations
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = img[y:y + h, x:x + w]

            # Perform OCR on cropped region
            text = pytesseract.image_to_string(cropped).strip()

            if text:  # Only consider non-empty text
                self.fullText += text + "\n"
                self.text_with_locations.append({
                    "text": text,
                    "bounding_box": (x, y, w, h)
                })

        return self.text_with_locations

    def export_to_file(self, filename="recognized.txt"):
        with open(filename, "w") as file:
            for item in self.text_with_locations:
                file.write(f"Text: {item['text']}\n")
                file.write(f"Bounding Box: {item['bounding_box']}\n")
                file.write("\n")

# Example usage
if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/Tesseract.exe'
    
    extractor = TextExtractor("Screenshot 2024-11-24 193229.png")
    text_with_locations = extractor.extract_text()
    
    for item in text_with_locations:
        print(f"Text: {item['text']}")
        print(f"Bounding Box: {item['bounding_box']}")
        print("---")
    
    extractor.export_to_file("recognized.txt")
