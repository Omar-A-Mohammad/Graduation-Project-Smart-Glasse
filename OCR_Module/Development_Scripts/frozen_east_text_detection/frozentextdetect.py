import cv2
import numpy as np
import pytesseract
from spellchecker import SpellChecker
from concurrent.futures import ThreadPoolExecutor
import os
import time
import sys

# Set up Tesseract executable path (adjust according to your setup)
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Load the pre-trained EAST model
if not os.path.exists("frozen_east_text_detection.pb"):
    raise FileNotFoundError("EAST model file not found.")
net = cv2.dnn.readNet("frozen_east_text_detection.pb")

# Initialize spell checker
spell = SpellChecker()

# Function to preprocess a region of interest (ROI)
def preprocess_roi(roi):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh

# Function to decode predictions
def decode_predictions(scores, geometry, min_confidence=0.5):
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(numCols):
            if scoresData[x] < min_confidence:
                continue

            offsetX, offsetY = x * 4.0, y * 4.0
            angle = anglesData[x]
            cos, sin = np.cos(angle), np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append([startX, startY, endX, endY])
            confidences.append(scoresData[x])

    return rects, confidences

# Function to perform OCR and spell checking on a region
def process_roi(roi):
    try:
        # Preprocess the ROI
        processed_roi = preprocess_roi(roi)

        # Perform OCR
        text = pytesseract.image_to_string(processed_roi, lang='eng')

        # Correct spelling errors
        corrected_text = " ".join([spell.correction(word) or word for word in text.split()])
        return corrected_text
    except Exception as e:
        print(f"Error processing ROI: {e}")
        return ""

# Function to detect text in the frame
def detect_text(frame, net, min_confidence=0.5):
    orig = frame.copy()
    H, W = frame.shape[:2]
    newW, newH = 320, 320  # Resize dimensions (must be multiple of 32)
    rW, rH = W / float(newW), H / float(newH)
    frame_resized = cv2.resize(frame, (newW, newH))

    # Create a blob and perform a forward pass
    blob = cv2.dnn.blobFromImage(frame_resized, 1.0, (newW, newH),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    scores, geometry = net.forward(["feature_fusion/Conv_7/Sigmoid",
                                     "feature_fusion/concat_3"])

    # Decode predictions and apply non-maxima suppression
    rects, confidences = decode_predictions(scores, geometry, min_confidence)
    boxes = cv2.dnn.NMSBoxes(rects, confidences, min_confidence, 0.4)

    results = []
    if len(boxes) > 0:
        for i in boxes:
            box = rects[i]
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1 * rW), int(y1 * rH), int(x2 * rW), int(y2 * rH)
            roi = orig[y1:y2, x1:x2]
            results.append((roi, (x1, y1, x2, y2), confidences[i]))

    return results

# Initialize video capture
cap = cv2.VideoCapture("http://192.168.100.7:8080/video")
if not cap.isOpened():
    raise RuntimeError("Failed to open video stream.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Retrying...")
            time.sleep(1)
            continue

        # Detect text regions in the frame
        detections = detect_text(frame, net)

        # Process detected regions in parallel
        texts = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            texts = list(executor.map(lambda det: process_roi(det[0]), detections))

        # Draw results on the frame
        for ((x1, y1, x2, y2), text, confidence) in zip([det[1] for det in detections], texts, [det[2] for det in detections]):
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{text} ({confidence:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Show the frame
        cv2.imshow("Real-Time Text Detector", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Exiting...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)