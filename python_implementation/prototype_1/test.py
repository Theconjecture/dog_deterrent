import pigpio
import time

pin = 18
steps = 10000
pulse_freq = 22000
freq_start = 20000
freq_end = 30000
duty = 50 * steps
sweep_time = 3
pulse_on, pulse_off = 0.5, 0.2


def sweep(start, end, sweep_time):
    try:
        while True:
            for freq in range(start, end+1, 10):
                pi.hardware_PWM(pin, freq, duty)
                time.sleep(sweep_time/(end-start))

            for freq in range(end, start-1,-10):
                pi.hardware_PWM(pin, freq, duty)
                time.sleep(sweep_time/(end-start))
    except KeyboardInterrupt:
        print("User interuptted")
    finally:
        pi.hardware_PWM(pin, 0, 0)
        pi.stop()


def set_sweep():
    start: int = int(input( "Enter starting frequency\n"))
    end: int = int( input( "Enter ending frequency\n")) 
    sweep_time: int = int( input("Enter sweep_time\n"))
    
    sweep(start, end, sweep_time)

def pulse(pulse_freq, pulse_on, pulse_off) -> None:
    try:
        while True:
            # Turn PWM ON
            pi.hardware_PWM(pin, pulse_freq, duty)
            time.sleep(pulse_on)

            # Turn PWM OFF
            pi.hardware_PWM(pin, 0, 0)
            time.sleep(pulse_off)
    except KeyboardInterrupt:

        print("user interuptted")
    finally:
        pi.hardware_PWM(pin, 0, 0)
        pi.stop()


def set_pulse() -> None:
    pulse_freq: int = int( input("Enter pulse_freq\n"))
    pulse_on: int = int( input("Enter pulse on time (in seconds)\n"))
    pulse_off: int = int( input("Enter pulse off time (in secoffds)\n"))

    pulse(pulse_freq, pulse_on, pulse_off)

def square_wave() -> None:
    freq: int = int(input("Enter the frequency: \n"))

    try:
        pi.hardware_PWM(pin, freq, duty)

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("user interuptted")

    finally:
        pi.hardware_PWM(pin, 0, 0)
        pi.stop()

def menu() -> None:
    option: int = 0
    print("""\nAssalamu Alaykum\n 
          ===================\n 
          Dog whistle system\n 
          ===================\n 
          Modes:\n 
          1. Continuous\n 
          2. Sweep\n 
          3. Pulsing\n 
          \n 
          (press 4 to quit)\n""")
    option = int(input())
    if option not in [1,2,3,4]:
        print("Invalid input")
        menu()
    else:
        match option:
            case 1:
                square_wave()
            case 2:
                set_sweep()
            case 3:
                set_pulse()
            case 4:
                raise SystemExit("Goodbye")
    
pi = pigpio.pi()

pi.set_mode(pin, pigpio.OUTPUT)
pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

menu()

"""

import numpy as np
from scipy.io.wavfile import write

# Parameters
sample_rate = 44100  # Hz
duration = 50.0       # seconds
frequency = 440.0    # A4 note (adjust as needed)
amplitude = 0.5      # 0 to 1.0 (avoid clipping)

# Generate sine wave
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM (-32768 to 32767)
sine_wave_int16 = np.int16(sine_wave * 32767)

# Save as WAV file
write("sine_wave.wav", sample_rate, sine_wave_int16)
"""
