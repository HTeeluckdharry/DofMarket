import cv2

def check_current_resolution():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(f"Current Resolution: {int(width)}x{int(height)}")

    cap.release()

if __name__ == "__main__":
    check_current_resolution()