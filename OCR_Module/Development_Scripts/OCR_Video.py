import threading
import queue
import time
import cv2
import OCR_Processor  # Your OCR processor class

def ocr_worker(frame_queue, ocr_processor, results_queue):
    """
    Worker function to process frames for OCR.
    """
    while True:
        # Get a frame from the queue
        if not frame_queue.empty():
            frame = frame_queue.get()

            # Perform OCR on the frame
            try:
                json_results = ocr_processor.perform_ocr(frame)
                results_queue.put((frame, json_results))  # Store the annotated frame and results
            except Exception as e:
                print(f"OCR Error: {e}")
                results_queue.put((frame, None))  # Store the original frame if OCR fails

        # Small delay to avoid busy-waiting
        time.sleep(0.1)

def main():
    # Initialize OCRProcessor
    ocr = OCR_Processor.OCRProcessor('C:/Program Files/Tesseract-OCR/Tesseract.exe')

    # Initialize video capture
    cap = cv2.VideoCapture("http://192.168.100.7:8080/video")
    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    # Create thread-safe queues for frames and results
    frame_queue = queue.Queue(maxsize=10)  # Limit queue size to avoid memory issues
    results_queue = queue.Queue()

    # Start the OCR worker thread
    ocr_thread = threading.Thread(target=ocr_worker, args=(frame_queue, ocr, results_queue), daemon=True)
    ocr_thread.start()

    frame_counter = 0
    ocr_frequency = 5  # Perform OCR every 5 frames

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Add frames to the OCR queue at the specified frequency
        if frame_counter % ocr_frequency == 0:
            if not frame_queue.full():  # Avoid overloading the queue
                frame_queue.put(frame)

        # Check for OCR results
        if not results_queue.empty():
            annotated_frame, json_results = results_queue.get()
            if json_results:
                print("OCR Results:", json_results)
                frame = annotated_frame  # Display the annotated frame

        # Display the frame
        cv2.imshow('Frame', frame)

        # Increment frame counter
        frame_counter += 1

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()