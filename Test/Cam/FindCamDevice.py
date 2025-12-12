# Test Camera each time
import cv2

for i in range(5):  
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(" Camera found at index ", i)
        else:
            print(" Camera at index", i ,"opened but no frame captured")
        cap.release()
    else:
        print("No camera at index", i)