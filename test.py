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

pi = pigpio.pi()

pi.set_mode(pin, pigpio.OUTPUT)
pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

try:

    while True:
        """
        for freq in range(freq_start,freq_end+1, 10):
            pi.hardware_PWM(pin, freq, duty)
            time.sleep(sweep_time/(freq_end-freq_start))

        for freq in range(freq_end,freq_start-1,-10):
            pi.hardware_PWM(pin, freq, duty)
            time.sleep(sweep_time/(freq_end-freq_start))
        """

        # Turn PWM ON
        pi.hardware_PWM(pin, pulse_freq, duty)
        time.sleep(pulse_on)

        # Turn PWM OFF
        pi.hardware_PWM(pin, 0, 0)
        time.sleep(pulse_off)


except KeyboardInterrupt:
    
    print("user interuppted")

finally:
    pi.hardware_PWM(pin, 0, 0)
    pi.stop()

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
