#!/usr/bin/env python3
import RPi.GPIO as GPIO

# Setup
GPIO.setmode(GPIO.BCM)  # BCM numbering (GPIO14 = pin 8)
GPIO.setup(14, GPIO.OUT)
current_state = False

print("GPIO14 Control - Press:")
print("1: Turn ON")
print("0: Turn OFF")
print("q: Quit")

try:
    while True:
        cmd = input("> ").strip().lower()
        
        if cmd == '1':
            GPIO.output(14, GPIO.HIGH)
            current_state = True
            print("GPIO14 ON")
        elif cmd == '0':
            GPIO.output(14, GPIO.LOW)
            current_state = False
            print("GPIO14 OFF")
        elif cmd == 'q':
            break
        else:
            print(f"Current state: {'ON' if current_state else 'OFF'}")

finally:
    GPIO.cleanup()
    print("\nGPIO cleaned up. Exiting.")
