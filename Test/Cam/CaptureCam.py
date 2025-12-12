import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not accessible")
else:
    ret, frame = cap.read()
    
    if ret:
        cv2.imshow('Captured Image', frame)
        print("Press any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to grab frame")


cap.release()