# This file holds the description of the functions
# to be generated from the pi 
"""
The formula is comprised of two waves, one carrier wave and another 
modulating wave, namely car and mod.

The resulting signal is the addition of both car + mod = sig
* note that mod is essentially a sinosoidal damping wave

car = A*sin(2*pi*f*x)
mod = B*exp(-beta(u+mod(x,1/pf))) * sin(2*n*pi*f*x)

Check the documentation for the parameter definitions
The values of each are:
    A = 3
    f = 24000
    B = 5.7
    beta = tf * ln(q)
    t = 3.4
    q = 100
    u = 0
    p = 1
    n = 50
"""
import subprocess
import numpy as np 
import pigpio
import time 
from scipy.io.wavfile import write

# initialize pigpio

pi = pigpio.pi()

# Parameters

f = 24000  # frequency
sample_rate = 16 * f 
period = 1/f # seconds

duration = 15 # seconds

# Carrier signal

A = 3       # amplitude
def carrier(x):
    car = A*np.sin(2*np.pi*f*np.array(x))
    return car

# Damping sinosoid

B = 5.7     # amplitude
t = 3.4
q = 100
beta = t * f * np.log(q)
u = 0
p = 1
n = 50      # nth harmonicbin

def modulation(x):
    mod = B*np.exp(-beta*(u+(np.mod(x,period)))) * np.sin(2*n*np.pi*f*x)
    return mod

# Generate the custom wave

# time stamps

t = np.linspace(0,duration, int(sample_rate * duration), endpoint = False)
carrier_wave = carrier(t)
modulating_wave = modulation(t)

custom_wave = carrier_wave + modulating_wave

audio_data = np.int16(custom_wave*10922)

# save as wav file
write("wave.wav", sample_rate, audio_data)
