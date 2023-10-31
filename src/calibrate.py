# =========== IMPORTS ===========

# imports for io
from gpiozero import LED, Button
from signal import pause

# imports for utilities and multithreading
from utils import geometric_mean
from time import sleep

# imports for getting people's audio input
from audio_input import get_avg_amplitude_of_samples

# imports for tts
from text_to_speech import play_audio

# =========== IO SETUP ===========
button = Button(27, hold_time=1)
visible_led = LED(23)

# =========== INITIALIZATION ===========
NUM_CALIBRATION_TRIALS = 3
warn_path = '../recordings/warn'

def calibrate_threshold():
    print("calibrating")
    
    play_audio(f'{warn_path}/talk.mp3')
    sleep(1)
    visible_led.on()
    talking_amp = get_avg_amplitude_of_samples(NUM_CALIBRATION_TRIALS)
    print("talk: ", talking_amp)
    visible_led.off()
    
    play_audio(f'{warn_path}/silent.mp3')
    sleep(1)
    visible_led.on()
    silence_amp = get_avg_amplitude_of_samples(NUM_CALIBRATION_TRIALS)
    visible_led.off()
    print("silence: ", silence_amp)

    threshold_avg = geometric_mean(talking_amp, silence_amp)
    print("threshold: ", threshold_avg)
    play_audio(f'{warn_path}/complete.mp3')

# =========== MAIN LOOP ===========
button.when_held = calibrate_threshold

pause()