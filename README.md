# 🥝🍓🍹DofMarket🍎🍌🍋
This project implements a fruit seller system using a **DOFBOT (6-DOF Robotic Arm)** .It uses Computer Vision (YOLO) to detect fruits and drop them into a basket using a pick-and-place mechanism.

## 💻 Software & Dependencies
* Python 3.x
* **OpenCV** (`opencv-python`)
* **PyTorch** (configured for ARM64)
* **Arm_Lib** (Yahboom proprietary library)

## ⚙️ How it Works

1.  **Initialisation:** The system moves the arm to a "Home/Scanning" position.
2.  **Detection:** The camera feeds video to the YOLO model.
3.  **Classification:**
    * If **Apple** is detected -> Trigger Sequence A.
    * If **Orange** is detected -> Trigger Sequence B.
4.  **Actuation:** the system executes a **hardcoded sequence of servo angles** read manually during the calibration phase.

## ⚠️ Known Issues & Limitations

During development, several challenges were encountered and documented:

* **VS Code Incompatibility:** The `Arm_Lib` library fails to import correctly when running inside Visual Studio Code's integrated terminal. **Solution:** Manually installled it.
* **Frame Rate (FPS):** Running YOLO on the CPU results in low FPS (~1-5 FPS).
  
## 🚀 Installation & Usage

1.  Install dependencies (ensure `Arm_Lib` is installed via the manufacturer instructions):
    ```bash
    pip3 install opencv-python torch torchvision
    ```

2. Have the model `fruit.pt` in `DofMarket/models`

3.  Run the script:
    ```bash
    sudo python3 fruitseller.py
    ```
## 🛠️ Model Training (Optional)

If you wish to train the model instead of using the provided `fruit.pt`:

1.  **Install Ultralytics:**
    ```bash
    pip install ultralytics
    ```

2.  **Prepare Dataset:**
    Download the dataset ( yolo11 zip to computer)
    ```bash
    curl -L https://universe.roboflow.com/office-robotic/fruit-box/dataset/1
    ```

## 🔮 Future Improvements
* [ ] Retrain model with Real fruits(Instead of fruit cubes)
* [ ] Convert model file in different format(e.g Tflite) for better frames.
* [ ] Implement real Inverse Kinematics for dynamic grabbing.
