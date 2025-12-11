#!/usr/bin/env python3
#coding=utf-8
import sys
import time
import threading
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO

# Try importing the Arm library (Handle errors if running without arm for testing)
try:
    from Arm_Lib import Arm_Device
    arm_available = True
except ImportError:
    print("WARNING: Arm_Lib not found.")
    arm_available = False

# CONFIGURATION & CONSTANTS

# Arm Config
MOVE_TIME = 1500
GRAB_TIME = 500
GRIPPER_OPEN = 40
GRIPPER_CLOSE = 138

# Positions
POS_DROP = [90, 110, 0, 10, 90, GRIPPER_OPEN]
POS_HOME = [90, 130, 30, 0, 90, GRIPPER_OPEN]

FRUIT_STATIONS = {
    'apple':      [65, 90, -15, 90, 90, GRIPPER_OPEN], 
    'banana':     [112, 72, 53, 46, 90, GRIPPER_OPEN],
    'kiwi':       [112, 90, -15, 90, 90, GRIPPER_OPEN],
    'lemon':      [90, 76, 51, 45, 90, GRIPPER_OPEN],
    'lychee':     [87, 100, -25, 90, 90, GRIPPER_OPEN],
    'strawberry': [65, 60, 70, 43, 90, GRIPPER_OPEN]
}

FRUIT_PRICES = {
    'apple': 20,
    'banana': 25,
    'kiwi': 30,
    'lemon': 40,
    'lychee': 50,
    'strawberry': 60
}

# AI Config
MODEL_PATH = '/home/pi/Documents/PythonCW/models/best.pt'
CAMERA_INDEX = 0

# HARDWARE CONTROL CLASS

class RoboticArmController:
    def __init__(self):
        if arm_available:
            self.Arm = Arm_Device()
            time.sleep(0.1)
        else:
            self.Arm = None

    def move_arm(self, angles, duration):
        if self.Arm:
            self.Arm.Arm_serial_servo_write6(angles[0], angles[1], angles[2], angles[3], angles[4], angles[5], duration)
            time.sleep((duration / 1000.0) + 0.1)
        else:
            print(f"[SIM] Moving to {angles} over {duration}ms")
            time.sleep((duration / 1000.0))

    def set_gripper(self, angle):
        if self.Arm:
            self.Arm.Arm_serial_servo_write(6, angle, 500)
            time.sleep(0.5)
        else:
            print(f"[SIM] Gripper set to {angle}")
            time.sleep(0.5)

    def run_pickup_sequence(self, pickup_angles, update_status_callback):
        
        # Executes the pickup logic using the specific pickup_angles passed in.
        
        # 1. Start from Home
        update_status_callback("Moving Home...")
        self.move_arm(POS_HOME, MOVE_TIME)
        self.set_gripper(GRIPPER_OPEN)

        # 2. Move to Fruit Position
        target_pos = list(pickup_angles)
        target_pos[5] = GRIPPER_OPEN 
        
        update_status_callback(f"Reaching for fruit...")
        self.move_arm(target_pos, MOVE_TIME)
        
        # 3. Grab
        update_status_callback("Grabbing...")
        self.set_gripper(GRIPPER_CLOSE)

        # 4. Lift Up 
        base_angle = pickup_angles[0]
        pos_lift = [base_angle, 130, 30, 0, 90, GRIPPER_CLOSE]
        
        update_status_callback("Lifting fruit...")
        self.move_arm(pos_lift, MOVE_TIME)

        # 5. Move to Drop Zone
        update_status_callback("Moving to drop zone...")
        drop_pos_closed = list(POS_DROP)
        
        drop_pos_closed[5] = GRIPPER_CLOSE
        self.move_arm(drop_pos_closed, MOVE_TIME) 

        # 6. Drop
        update_status_callback("Dropping fruit...")
        self.set_gripper(GRIPPER_OPEN)

        # 7. Return Home
        update_status_callback("Returning Home...")
        self.move_arm(POS_HOME, MOVE_TIME)
        update_status_callback("Ready")

# GUI APPLICATION

class DofMarketApp:
    def __init__(self, root, arm_controller):
        self.root = root
        self.root.title("DofMarket")
        
        # Center the window
        window_width = 1280
        window_height = 720
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.arm_controller = arm_controller
        self.is_busy = False # Lock to prevent double clicking
        self.total_cost = 0
        
        # Theme Config
        self.bg_color = "#2c2c2c"
        self.panel_color = "#383838"
        self.text_color = "#ffffff"
        self.accent_color = "#4a90e2"
        
        self.root.configure(bg=self.bg_color)

        #  AI / Video Setup
        self.model = None  
        try:
            print("Loading YOLO model...")
            self.model = YOLO(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("WARNING: Running without AI detection.")
            

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 30)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -5)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 30)

        # OPTIMISATION 
        self.SKIP_FRAMES = 30
        self.frame_count = 0
        self.last_detections = [] # Stores (box_coords, label) tuples

        
        #  GUI Layout 
        
        # Left Side: Video Feed
        self.video_frame = tk.Frame(root, width=640, height=480, bg="black")
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack()

        # Right Side: Controls
        self.control_panel = tk.Frame(root, width=300, bg=self.panel_color)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        tk.Label(self.control_panel, text="Fruit Selection", font=("Arial", 20, "bold"), 
                 bg=self.panel_color, fg=self.text_color).pack(pady=20)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("System Ready")
        self.status_label = tk.Label(self.control_panel, textvariable=self.status_var, 
                                     font=("Arial", 14), bg=self.panel_color, fg="#00ff00")
        self.status_label.pack(pady=10)

        # Total Cost Label
        self.cost_var = tk.StringVar()
        self.cost_var.set("Total Cost: Rs 0")
        self.cost_label = tk.Label(self.control_panel, textvariable=self.cost_var,
                                   font=("Arial", 16, "bold"), bg=self.panel_color, fg="#ffd700")
        self.cost_label.pack(pady=10)

        # FPS Label
        self.fps_var = tk.StringVar()
        self.fps_label = tk.Label(self.control_panel, textvariable=self.fps_var, 
                                  font=("Courier", 12), bg=self.panel_color, fg=self.text_color)
        self.fps_label.pack(pady=5)

        # Buttons Container
        self.btn_container = tk.Frame(self.control_panel, bg=self.panel_color)
        self.btn_container.pack(pady=20)

        # Generate Buttons dynamically from dictionary
        self.buttons = {}
        for fruit_name in FRUIT_STATIONS.keys():
            price = FRUIT_PRICES.get(fruit_name, 0)
            btn = tk.Button(self.btn_container, 
                            text=f"Pick {fruit_name.capitalize()} (Rs {price})", 
                            font=("Arial", 12), 
                            bg=self.accent_color,
                            fg="white",
                            activebackground="#357abd",
                            activeforeground="white",
                            width=20,
                            height=2,
                            command=lambda f=fruit_name: self.start_pick_thread(f))
            btn.pack(pady=5)
            self.buttons[fruit_name] = btn

        # Stop Button
        # Bottom Controls (Reset & Exit)
        self.bottom_controls = tk.Frame(self.control_panel, bg=self.panel_color)
        self.bottom_controls.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

        tk.Button(self.bottom_controls, text="RESET COST", bg="orange", fg="white", font=("Arial", 12, "bold"),
                  command=self.reset_cost).pack(side=tk.LEFT, padx=10, expand=True)

        tk.Button(self.bottom_controls, text="FINISH", bg="#28a745", fg="white", font=("Arial", 12, "bold"),
                  command=self.show_checkout_screen).pack(side=tk.LEFT, padx=10, expand=True)

        tk.Button(self.bottom_controls, text="EXIT", bg="red", fg="white", font=("Arial", 12, "bold"), 
                  command=self.on_close).pack(side=tk.RIGHT, padx=10, expand=True)

        # Start Loops 
        self.prev_frame_time = 0
        self.update_video()

    def show_checkout_screen(self):
       
        self.is_busy = True # Stop any arm threads if possible
        
        # Stop video
        if self.cap.isOpened():
            self.cap.release()
            
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configure checkout UI
        self.root.configure(bg=self.bg_color)
        
        # Container for centering
        container = tk.Frame(self.root, bg=self.bg_color)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(container, text="Thank you for your purchase!", 
                 font=("Arial", 30, "bold"), bg=self.bg_color, fg="#4a90e2").pack(pady=30)
                 
        tk.Label(container, text=f"Total Amount: Rs {self.total_cost}", 
                 font=("Arial", 25, "bold"), bg=self.bg_color, fg="#ffd700").pack(pady=20)
                 
        tk.Button(container, text="EXIT", bg="red", fg="white", font=("Arial", 14, "bold"), 
                  width=15, command=self.on_close).pack(pady=50)
                  
        # Footer
        tk.Label(self.root, text="Thank you for using DofMarket", 
                 font=("Arial", 12, "italic"), bg=self.bg_color, fg="#888888").pack(side=tk.BOTTOM, pady=20)




    def reset_cost(self):
        """Resets the total cost to 0."""
        self.total_cost = 0
        self.cost_var.set("Total Cost: Rs 0")
        self.status_var.set("Cost Reset")

    def start_pick_thread(self, fruit_name):
        
        if self.is_busy:
            messagebox.showwarning("Busy", "Arm is currently moving! Please wait.")
            return

        self.is_busy = True
        self.disable_buttons()
        
        # Create a thread for the blocking arm logic
        threading.Thread(target=self.pick_logic, args=(fruit_name,), daemon=True).start()

    def pick_logic(self, fruit_name):
        """The actual logic running in the background thread."""
        try:
            print(f"Starting sequence for {fruit_name}")
            
            # Add to cost
            price = FRUIT_PRICES.get(fruit_name, 0)
            self.total_cost += price
            self.status_var.set(f"Picking {fruit_name}...")
            # Schedule GUI update for cost in the main thread
            self.root.after(0, lambda: self.cost_var.set(f"Total Cost: Rs {self.total_cost}"))

            angles = FRUIT_STATIONS[fruit_name]
            
            self.arm_controller.run_pickup_sequence(angles, self.update_status)
            
        except Exception as e:
            print(f"Error in pick thread: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.is_busy = False
            self.enable_buttons()

    def update_status(self, text):
        self.status_var.set(text)

    def disable_buttons(self):
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED)

    def enable_buttons(self):
        # We need to use root.after because this might be called from the thread
        self.root.after(0, self._enable_buttons_main_thread)

    def _enable_buttons_main_thread(self):
        for btn in self.buttons.values():
            btn.config(state=tk.NORMAL)

    def update_video(self):
        """
        Captures frame, runs YOLO intermittently, and updates the GUI label.
        Optimized to skip frames for detection but draw persisted boxes.
        """
        ret, frame = self.cap.read()
        
        if ret:
            # 1. Run heavy detection every SKIP_FRAMES
            if self.model and (self.frame_count % self.SKIP_FRAMES == 0):
                # Run inference with stream=True for speed, smaller img size
                results = self.model(frame, conf=0.2, imgsz=640, stream=True, verbose=False)
                
                # Reset detections list
                self.last_detections = []
                
                # Process results
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        # Coordinates
                        b = box.xyxy[0].cpu().numpy().astype(int)
                        # Class & Confidence
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        label_text = f"{self.model.names[cls]} {conf:.2f}"
                        self.last_detections.append((b, label_text))
            
            # 2. Draw the saved boxes on EVERY frame
            for (b, label_text) in self.last_detections:
                x1, y1, x2, y2 = b
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, (0, 255, 0), 2)

            self.frame_count += 1

            # 3. Calculate FPS
            new_frame_time = time.time()
            if new_frame_time - self.prev_frame_time > 0:
                fps = 1 / (new_frame_time - self.prev_frame_time)
            else:
                fps = 0
            self.prev_frame_time = new_frame_time
            self.fps_var.set(f"FPS: {int(fps)}")

            # 4. Convert image for Tkinter (OpenCV BGR -> PIL RGB -> ImageTk)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_image)
            
            # Resize 
            img = img.resize((640, 480), Image.Resampling.LANCZOS)
            
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Schedule the next update (10ms = 100fps target for GUI refresh)
        self.root.after(10, self.update_video)

    def on_close(self):
        # Cleanup resources
        print("Closing application...")
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    # Initialise Hardware
    bot_arm = RoboticArmController()

    # Initialise GUI
    root = tk.Tk()
    app = DofMarketApp(root, bot_arm)
    
    # Handle window close button (X)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    root.mainloop()
