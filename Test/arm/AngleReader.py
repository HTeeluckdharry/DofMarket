#!/usr/bin/env python3
#coding=utf-8
import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()

def main():
    print("---------------------------------------")
    print("      DOFBOT Manual Angle Reader       ")
    print("---------------------------------------")
    print("1. Torque will be turned OFF.")
    print("2. Move the arm manually to desired positions.")
    print("3. Angles will print below.")
    print("4. Press Ctrl+C to exit.")
    print("---------------------------------------")
    
    time.sleep(2)
    
    # Turn off torque so you can move servos by hand
    # 0 = Off (Limp), 1 = On (Stiff)
    Arm.Arm_serial_set_torque(0)
    
    try:
        while True:
            # Read all 6 servos
            s1 = Arm.Arm_serial_servo_read(1)
            s2 = Arm.Arm_serial_servo_read(2)
            s3 = Arm.Arm_serial_servo_read(3)
            s4 = Arm.Arm_serial_servo_read(4)
            s5 = Arm.Arm_serial_servo_read(5)
            s6 = Arm.Arm_serial_servo_read(6)
            
            # Check for read errors (None)
            if None in [s1, s2, s3, s4, s5, s6]:
                print("Read Error - Check connections")
            else:
                print(f"[{s1}, {s2}, {s3}, {s4}, {s5}, {s6}]")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        # Optional: Turn torque back on before quitting to hold position
        # Arm.Arm_serial_set_torque(1) 

if __name__ == '__main__':
    main()