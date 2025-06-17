import cv2
import numpy as np
from ultralytics import YOLO
import pandas as pd
from sklearn.cluster import KMeans
from scipy.spatial import distance
import matplotlib.pyplot as plt
import json
from IPython.display import Image, display

# Load model and color data (same as before)
model = YOLO("yolo11n.pt")
colors_df = pd.read_csv("C:/Users/mahmoy2/OneDrive - Medtronic PLC/Downloads/Graduation-Project-Smart-Glasses/Color Detection/colors.csv", header=None)
colors_df.columns = ['ColorName', 'Unused', 'Hex', 'R', 'G', 'B']
colors_df = colors_df.drop(columns=['Unused'])

def get_closest_color_name(rgb):
    rgb = np.array(rgb)
    colors_df['distance'] = colors_df.apply(
        lambda row: distance.euclidean((row['R'], row['G'], row['B']), rgb),
        axis=1
    )
    return colors_df.loc[colors_df['distance'].idxmin(), 'ColorName']

def detect_color(image, is_traffic_light=False):
    # Focus on center region for traffic lights (avoid casing color)
    if is_traffic_light:
        h, w = image.shape[:2]
        image = image[h//4:3*h//4, w//4:3*w//4]

    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # More accurate HSV ranges for traffic lights
    if is_traffic_light:
        # Define masks for each color with tighter ranges
        masks = {
            "Red": [
                cv2.inRange(hsv, (0, 150, 100), (10, 255, 255)),
                cv2.inRange(hsv, (160, 150, 100), (179, 255, 255))
            ],
            "Yellow": cv2.inRange(hsv, (20, 150, 100), (30, 255, 255)),
            "Green": cv2.inRange(hsv, (40, 100, 100), (90, 255, 255))
        }

        # Combine red masks
        red_mask = cv2.bitwise_or(masks["Red"][0], masks["Red"][1])

        # Get pixel counts
        counts = {
            "Red": cv2.countNonZero(red_mask),
            "Yellow": cv2.countNonZero(masks["Yellow"]),
            "Green": cv2.countNonZero(masks["Green"])
        }

        # Only return a color if significant pixels found
        max_color = max(counts, key=counts.get)
        return max_color if counts[max_color] > 50 else "Unknown"

    # For non-traffic lights: improved clustering
    pixels = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).reshape(-1, 3)
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(pixels)

    # Get the largest cluster, ignoring very dark/bright clusters
    cluster_sizes = np.bincount(kmeans.labels_)
    valid_clusters = [i for i, center in enumerate(kmeans.cluster_centers_)
                     if not (np.mean(center) < 30 or np.mean(center) > 220)]

    if not valid_clusters:
        return "Unknown"

    dominant_idx = valid_clusters[np.argmax(cluster_sizes[valid_clusters])]
    dominant_color = kmeans.cluster_centers_[dominant_idx].astype(int)

    return get_closest_color_name(dominant_color)

def recognize_object(image_path):
    results = model(image_path)
    detected_objects = []

    for detection in results[0].boxes:
        cls = int(detection.cls.item())
        x1, y1, x2, y2 = map(int, detection.xyxy[0].tolist())
        label = results[0].names[cls]
        detected_objects.append({
            "label": label,
            "bbox": (x1, y1, x2, y2),
            "confidence": float(detection.conf.item())
        })

    return detected_objects

def main(image_path):
    output = {
        "image_path": image_path,
        "detected_objects": []
    }

    image = cv2.imread(image_path)
    if image is None:
        output["error"] = "Unable to load image"
        return json.dumps(output, indent=4)

    detected_objects = recognize_object(image_path)

    for obj in detected_objects:
        x1, y1, x2, y2 = obj["bbox"]
        roi = image[y1:y2, x1:x2]

        if obj["label"] == "traffic light":
            color = detect_color(roi, is_traffic_light=True)
            plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            plt.title(f"Traffic Light: {color}")
            plt.axis("off")
            plt.show()
        else:
            color = detect_color(roi)

        obj["color"] = color
        output["detected_objects"].append(obj)

    return json.dumps(output, indent=4)





# Test with your image
result = main("C:/Users/mahmoy2/OneDrive - Medtronic PLC/Downloads/Graduation-Project-Smart-Glasses/Color Detection/traffic light yellow.jpg")
display(Image(filename="C:/Users/mahmoy2/OneDrive - Medtronic PLC/Downloads/Graduation-Project-Smart-Glasses/Color Detection/traffic light yellow.jpg"))
print("________________________________________")
print(result)
with open("results.json", "w") as f:
    f.write(result)
