import os
from ultralytics import YOLO
import cv2
import time


MODEL_PATH = '/home/pi/Documents/PythonCW/models/fruit.pt'
model = YOLO(MODEL_PATH)

# Open the webcam
cap = cv2.VideoCapture(1)

# Lower resolution for speed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

SKIP_FRAMES = 30         
frame_count = 0          
last_detections = []     # Variable to store the boxes between detections

# Variables for FPS calculation
prev_frame_time = 0
new_frame_time = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

   
    if frame_count % SKIP_FRAMES == 0:
        
        results = model(frame, conf=0.5, imgsz=320, stream=True, verbose=False)
        
     
        last_detections = []
        
 
        for r in results:
            boxes = r.boxes
            for box in boxes:
               
                b = box.xyxy[0].cpu().numpy().astype(int)
                
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{model.names[cls]} {conf:.2f}"
                
            
                last_detections.append((b, label))

   
    for (b, label) in last_detections:
        x1, y1, x2, y2 = b
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (0, 255, 0), 2)

    frame_count += 1

    
    new_frame_time = time.time()
    if new_frame_time - prev_frame_time > 0:
        fps = 1 / (new_frame_time - prev_frame_time)
    else:
        fps = 0
    prev_frame_time = new_frame_time

   
    cv2.putText(frame, f"FPS: {int(fps)}", (7, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (100, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Fruit Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()