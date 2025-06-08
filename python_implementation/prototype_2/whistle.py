import RPi.GPIO as GPIO
import time

BUZZER_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def start_whistle():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def stop_whistle():
    GPIO.output(BUZZER_PIN, GPIO.LOW)
