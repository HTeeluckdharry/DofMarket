#!/usr/bin/env python3
#coding=utf-8
import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(0.1)


ID1 = 90 # Base
ID2 = 130 # Shoulder
ID3 = 30 # Elbow
ID4 = 0 # Wrist Pitch
ID5 = 90 # Wrist Roll (usually 90)
ID6 = 90 # Gripper (90 = Open, 126 = Close)

MOVE_TIME = 1500 



def main():

    print("--- Manual Move Start ---")
    print(f"Moving to: [{ID1}, {ID2}, {ID3}, {ID4}, {ID5}, {ID6}]")

    # Send command to all 6 servos
    Arm.Arm_serial_servo_write6(ID1, ID2, ID3, ID4, ID5, ID6, MOVE_TIME)

    # Wait for move to finish
    time.sleep((MOVE_TIME / 1000.0) + 0.1)
    print("--- Position Reached ---")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")