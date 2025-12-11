import os
from ultralytics import YOLO

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DATA_DIR = os.path.join(ROOT_DIR, 'dataset')

# Output Paths
MODEL_DIR = os.path.join(ROOT_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    # 1. Setup Data Configuration
    yaml_file = os.path.join(DATA_DIR, 'data.yaml')

    if not os.path.exists(yaml_file):
        print(f" Error: Could not find dataset config at {yaml_file}")
        return

    # 2. Load the Model
    print("Loading YOLO11 Nano Model")
    model = YOLO('yolo11n.pt')

    # 3. Train with Augmentation
    print(f" Starting Training")
    results = model.train(
        data=yaml_file,
        epochs=100,
        imgsz=640,
        batch=32,
        patience=15,
        project=MODEL_DIR,
        name='fruit_yolo11',
        exist_ok=True,
        device='0',

        # Augmentation Hyperparameters
        degrees=15.0,  # Rotate images +/- 15 degrees
        translate=0.1,  # horizontally/vertically by 10%
        scale=0.5,  # Scale image gain (zoom in/out) by 50%
        fliplr=0.5,  # horizontal flip
        flipud=0.0,  # Vertical flip
        mosaic=1.0,  # Mosaic augmentation (takes 4 random images from your dataset and stitches them into one grid)

        #  Color Augmentation
        hsv_h=0.015,  # Hue
        hsv_s=0.7,  # Saturation
        hsv_v=0.4,  # Value of Brightness
    )

    # 4. Validate & Print Accuracy
    print("\n CALCULATING ACCURACY ")
    metrics = model.val()

    # Print the important numbers
    print(f"mAP@50 (Detection Accuracy): {metrics.box.map50:.2f}")
    print(f"mAP@50-95 (Precision Accuracy): {metrics.box.map:.2f}")

    print(f"\nTraining Complete. Model located at:")
    print(f"models/fruit_detect_run/weights/best.pt")


if __name__ == '__main__':
    main()