# =========== IMPORTS ===========

# imports for io
from gpiozero import LED, Button, MotionSensor
from signal import pause

# imports for utilities
import os
from utils import geometric_mean
from time import sleep, perf_counter
from random import randint

# imports for gpt
from gpt import reset_pumpkin_gpt, get_pumpkin_response, trigger_pumpkin_ask_question

# imports for stt
from audio_input import get_avg_amplitude_of_samples, get_audio_input, get_audio_input_multiprocessing

# imports for tts
from text_to_speech import tts, tts_high_quality, play_audio

# =========== IO SETUP ===========
red_led = LED(22)
green_led = LED(17)
visible_led = LED(23)
button = Button(27, hold_time=1)
pir = MotionSensor(18)

# =========== GLOBALS AND CONSTANTS ===========
# IO
SERVO_MIN = 0
SERVO_MAX = 10
# audio input
THRESHOLD_AVG = None
# THRESHOLD_AVG = 0.03496395 # TODO: delete
NUM_CALIBRATION_TRIALS = 3
# gpt
messages = reset_pumpkin_gpt()
# tts
highQualityTts = False # flip flag to use high vs. low quality TTS
ttsExtension = 'wav' if highQualityTts else 'mp3'

recording_path = '../recordings'
pumpkin_start_path = recording_path + '/pumpkin_start'
pumpkin_response_path = recording_path + '/pumpkin_response'
pumpkin_trick_path = recording_path + '/pumpkin_trick'
user_path = recording_path + '/user'
warn_path = recording_path + '/warn'

pumpkin_start_file_index = sorted(os.listdir(pumpkin_start_path), reverse=True)[0][0] if sorted(os.listdir(pumpkin_start_path)) else 0
pumpkin_trick_file_index = sorted(os.listdir(pumpkin_trick_path), reverse=True)[0][0] if sorted(os.listdir(pumpkin_trick_path)) else 0

def get_pumpkin_file_name(start=False, random=False, trick=False):
    if not start: return f'{pumpkin_response_path}/pumpkin.{ttsExtension}'
    
    global pumpkin_start_file_index
    global pumpkin_trick_file_index
    path = pumpkin_start_path if not trick else pumpkin_trick_path
    index = pumpkin_start_file_index if not trick else pumpkin_trick_file_index
    
    if random: return f'{path}/{randint(0,9)}pumpkin.{ttsExtension}'
    
    filename = f'{path}/{index}pumpkin.{ttsExtension}'
    index += 1
    return filename

# =========== INITIALIZATION ===========
def reset_io():
    red_led.off()
    green_led.off()
    visible_led.off()
    pir.wait_for_no_motion()
reset_io()

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

def run_main():
    print("-------------- START --------------")
    if not THRESHOLD_AVG:
        print("Calibrate threshold!")
        play_audio(f'{warn_path}/calibrate_threshold.mp3')
        for i in range(0,5):
            visible_led.on()
            sleep(0.3)
            visible_led.off()
            sleep(0.3)
        return
    # reset pumpkin gpt's context
    messages = reset_pumpkin_gpt()
    pumpkin_audio_file = None
    
    # startle person by talking for the first time
    if pumpkin_start_file_index < 10:
        pumpkin_audio_file = get_pumpkin_file_name(start=True)
        tts(get_pumpkin_response(messages), pumpkin_audio_file)
    else:
        pumpkin_audio_file = get_pumpkin_file_name(start=True, random=True)
    play_audio(pumpkin_audio_file)
    
    # listen to person's response and add to pumpkin gpt's context
    messages.append({"role": "user", "content": get_audio_input(THRESHOLD_AVG)})
    
    # pumpkin gpt responds to person
    pumpkin_audio_file = get_pumpkin_file_name()
    tts(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio(pumpkin_audio_file)
    
    # listen to person again
    messages.append({"role": "user", "content": get_audio_input(THRESHOLD_AVG)})
    
    # pumpkin gpt responds and asks "trick or treat"
    tts(trigger_pumpkin_ask_question(messages), pumpkin_audio_file)
    if "treat" in get_audio_input(THRESHOLD_AVG):
        # dispense
        print("Dispensing candy!!")
        sleep(5)
    if "trick" in get_audio_input(THRESHOLD_AVG):
        if pumpkin_trick_file_index < 10:
            messages.append({"role": "system", "content": "Create a short, one sentence joke about Halloween."})
            pumpkin_audio_file = get_pumpkin_file_name(trick=True)
            tts(get_pumpkin_response(messages), pumpkin_audio_file)
        else:
            pumpkin_audio_file = get_pumpkin_file_name(trick=True, random=True)
        play_audio(pumpkin_audio_file)

    print("-------------- END --------------")

# =========== MAIN LOOP ===========
button.when_held = calibrate_threshold
pir.when_motion = run_main

pause()