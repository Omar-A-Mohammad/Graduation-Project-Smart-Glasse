from ultralytics import YOLO

# Load a COCO-pretrained YOLO11 model
model = YOLO("Currency_Module/cur_n100_runs/best.pt")   ### Replace with best.pt or last.pt

# Run inference
results = model("Currency_Module/001456598.jpg")  #, save=True

# Prepare

import json

# Prepare
detections = []

for result in results:
    for box in result.boxes:
        
        x_center = float(box.xywh[0][0])
        y_center = float(box.xywh[0][1])
        width = float(box.xywh[0][2]) 
        height = float(box.xywh[0][3])

        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        detections.append({
            "text": class_name,
            "bbox": {
                "x": x_center,
                "y": y_center,
                "width": width,
                "height": height
            }
        })

# Save
json_output = "output_2.json"
with open(json_output, "w") as f:
    json.dump(detections, f, indent=4)

#View
with open("output_2.json") as f:
    data = json.load(f)

print(data)