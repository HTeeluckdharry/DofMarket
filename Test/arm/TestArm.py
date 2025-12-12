#!/usr/bin/env python3
#coding=utf-8
import time
from Arm_Lib import Arm_Device

# Initialise the Arm
Arm = Arm_Device()
time.sleep(0.1)


# Time for movements (milliseconds)
MOVE_TIME = 1800  
GRAB_TIME = 500

# Gripper Angles (ID 6)
GRIPPER_OPEN = 90
GRIPPER_CLOSE = 126


# 1. Home Position 
POS_HOME = [90, 90, 90, 90, 90, GRIPPER_OPEN]

# 2. Approach Position
POS_APPROACH = [90, 45, 140, 45, 90, GRIPPER_OPEN]

# 3. Grab Position 
POS_GRAB = [89, 51, 30, 29, 89, GRIPPER_OPEN]

# 4. Lift Position (
POS_LIFT = [132, 53, 28, 29, 89, GRIPPER_CLOSE]

# 5. Drop Location
POS_DROP_APPROACH = [45, 90, 125, 45, 90, GRIPPER_CLOSE]

def move_arm(angles, duration):
    
    Arm.Arm_serial_servo_write6(
        angles[0], angles[1], angles[2], angles[3], angles[4], angles[5], 
        duration
    )
    time.sleep((duration / 1000.0) + 0.1)

def set_gripper(angle):
    Arm.Arm_serial_servo_write(6, angle, 500)
    time.sleep(0.5)

def main():
    print("--- Start Fruit Picking ---")
    
    # 1. Reset to Center
    print("1. Home Position")
    move_arm(POS_HOME, 1000)
    
    # 2. Open Gripper
    set_gripper(GRIPPER_OPEN)

    # 3. Approach
    print("3. Approaching Target")
    move_arm(POS_APPROACH, MOVE_TIME)

    # 4. Lower to Grab Position (ALL 0)
    print("4. Lowering to Grab (ID2=0, ID3=0, ID4=0)")
    move_arm(POS_GRAB, MOVE_TIME)

    # 5. Grab
    print("5. Grabbing Fruit")
    set_gripper(GRIPPER_CLOSE)
    
    # 6. Lift Up
    print("6. Lifting Fruit")
    move_arm(POS_LIFT, MOVE_TIME)

    # 7. Move to Drop
    print("7. Moving to Drop Zone")
    move_arm(POS_DROP_APPROACH, 1500)

    # 8. Drop
    print("8. Dropping Fruit")
    set_gripper(GRIPPER_OPEN)

    # 9. Return Home
    print("9. Returning Home")
    move_arm(POS_HOME, 1500)
    
    print("--- Sequence Complete ---")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 90, 1000)