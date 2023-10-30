# =========== IMPORTS ===========

# imports for io and
from gpiozero import LED, Button, MotionSensor
from signal import pause

# imports for utilities and multithreading
from utils import geometric_mean
from time import sleep

# imports for getting people's audio input
from audio_input import get_avg_amplitude_of_samples

# =========== IO SETUP ===========
talk_led = LED(22)
silence_led = LED(17)
button = Button(27, hold_time=1)

# =========== INITIALIZATION ===========
talk_led.off()
silence_led.off()
NUM_CALIBRATION_TRIALS = 3

def calibrate_threshold():
    print("calibrating")
    
    sleep(1)
    talk_led.on()
    talking_amp = get_avg_amplitude_of_samples(NUM_CALIBRATION_TRIALS)
    print("talk: ", talking_amp)
    talk_led.off()
    
    sleep(1)
    silence_led.on()
    silence_amp = get_avg_amplitude_of_samples(NUM_CALIBRATION_TRIALS)
    silence_led.off()
    print("silence: ", silence_amp)

    threshold_avg = geometric_mean(talking_amp, silence_amp)
    print("threshold: ", threshold_avg)

button.when_held = calibrate_threshold

pause()