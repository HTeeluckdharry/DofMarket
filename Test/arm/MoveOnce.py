#!/usr/bin/env python3
#coding=utf-8
import time
from Arm_Lib import Arm_Device

# Initialise the Arm
Arm = Arm_Device()
time.sleep(0.1)


# 1. HOME POSITION 
home_pos = [90, 130, 30, 0, 90, 90]

# 2. TARGET POSITION 
target_pos = [65, 90, -15, 90, 90, 40] 

MOVE_TIME = 1500 



def main():
    # 1: Go to Home Position
    print("--- Moving to Home Position ---")
    print(f"Home Data: {home_pos}")
    
   
    Arm.Arm_serial_servo_write6(*home_pos, MOVE_TIME)
    
    # Wait for move to finish
    time.sleep((MOVE_TIME / 1000.0) + 0.5)

    # 2: Go to Target Position
    print("--- Moving to Target Position ---")
    print(f"Target Data: {target_pos}")
    
    # Send command to all 6 servos using the target list
    Arm.Arm_serial_servo_write6(*target_pos, MOVE_TIME)
    
    # Wait for move to finish
    time.sleep((MOVE_TIME / 1000.0) + 0.1)
    
    print("--- Target Reached ---")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")