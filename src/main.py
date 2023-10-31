# =========== IMPORTS ===========

# imports for io
from gpiozero import LED, Button, MotionSensor, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause

# imports for utilities
import os
from utils import geometric_mean
from time import sleep, perf_counter
from random import randint

# imports for gpt
from gpt import reset_pumpkin_gpt, get_pumpkin_response

# imports for stt
from audio_input import get_avg_amplitude_of_samples
from audio_input_v2 import reset, get_audio

# imports for tts
from text_to_speech import tts, tts_high_quality, play_audio

# =========== IO SETUP ===========
red_led = LED(22)
green_led = LED(17)
visible_led = LED(23)
pir = MotionSensor(4)
servo = Servo(18)

# =========== GLOBALS AND CONSTANTS ===========
# IO
SERVO_MIN = -1
SERVO_MAX = 1
# audio input
# THRESHOLD_AVG = None
THRESHOLD_AVG = 0.01893387
# gpt
messages = reset_pumpkin_gpt()
# tts
highQualityTts = False # flip flag to use high vs. low quality TTS
ttsExtension = 'wav' if highQualityTts else 'mp3'
def tts_call(text, file):
    print('text being converted to speech: ', text)
    if highQualityTts:
        tts_high_quality(text, file)
    else:
        tts(text, file)

recording_path = '../recordings'
pumpkin_start_path = recording_path + '/pumpkin_start'
pumpkin_response_path = recording_path + '/pumpkin_response'
pumpkin_treat_path = recording_path + '/pumpkin_treat'
pumpkin_trick_path = recording_path + '/pumpkin_trick'
user_path = recording_path + '/user'
warn_path = recording_path + '/warn'

pumpkin_start_file_index = int(sorted(os.listdir(pumpkin_start_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_start_path)) else 0
pumpkin_treat_file_index = int(sorted(os.listdir(pumpkin_treat_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_treat_path)) else 0
pumpkin_trick_file_index = int(sorted(os.listdir(pumpkin_trick_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_trick_path)) else 0

def get_pumpkin_file_name(path=pumpkin_response_path):
    if path == pumpkin_response_path:
        return f'{pumpkin_response_path}/pumpkin.{ttsExtension}'
    
    global pumpkin_start_file_index
    global pumpkin_treat_file_index
    global pumpkin_trick_file_index
    
    index_map = {
        pumpkin_start_path: pumpkin_start_file_index,
        pumpkin_treat_path: pumpkin_treat_file_index,
        pumpkin_trick_path: pumpkin_trick_file_index
    }
    
    index = index_map[path]
    
    if random: return f'{path}/{randint(0,9)}pumpkin.{ttsExtension}'
    
    index += 1
    filename = f'{path}/{index}pumpkin.{ttsExtension}'
    return filename

def get_audio_io():
    visible_led.on()
    reset(THRESHOLD_AVG)
    transcript = get_audio()
    visible_led.off()
    return transcript

# =========== INITIALIZATION ===========
def reset_io():
    red_led.off()
    green_led.off()
    visible_led.off()
    pir.wait_for_no_motion()
reset_io()       

def run_main():
    print("-------------- START --------------")
    # reset pumpkin gpt's context
    messages = reset_pumpkin_gpt()
    # pumpkin_audio_file = None
    
    # startle person by talking for the first time
    # if pumpkin_start_file_index < 10:
        # pumpkin_audio_file = get_pumpkin_file_name(start=True)
        # tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    # else:
        # pumpkin_audio_file = get_pumpkin_file_name(start=True, random=True)
    # print('pumpkin start audio file name: ', pumpkin_audio_file)
    
    pumpkin_audio_file = get_pumpkin_file_name()
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio(pumpkin_audio_file)
    
    # listen to person's response and add to pumpkin gpt's context
    messages.append({"role": "user", "content": get_audio_io()})
    
    # pumpkin gpt responds to person
    pumpkin_audio_file = get_pumpkin_file_name()
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio(pumpkin_audio_file)
    
    # listen to person again
    messages.append({"role": "user", "content": get_audio_io()})
    
    # pumpkin gpt responds and asks "trick or treat"
    messages.append({"role": "system", "content": "Now naturally shift the conversation to asking the kids 'Would you like a trick or a treat?'"})
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio(pumpkin_audio_file)
    if "treat" in get_audio_io():
        play_audio(f'{recording_path}/dispense.{ttsExtension}')
        print("Dispensing candy!!")
        servo.value = SERVO_MIN
        sleep(1)
        servo.value = SERVO_MAX
        sleep(1)
        servo.value = SERVO_MIN
        sleep(1)
        servo.value = SERVO_MAX
        sleep(1)
    else:
        # if pumpkin_trick_file_index < 10:
            # messages.append({"role": "system", "content": "Create a short, one sentence joke about Halloween."})
            # pumpkin_audio_file = get_pumpkin_file_name()
            # tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
        # else:
            # pumpkin_audio_file = get_pumpkin_file_name()
        messages.append({"role": "system", "content": "Create a short, one sentence joke about Halloween."})
        pumpkin_audio_file = get_pumpkin_file_name()
        tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
        play_audio(pumpkin_audio_file)

    print("-------------- END --------------")
    # wait for people to leave
    messages.append({"role": "system", "content": "Now tell the kid to shoo with a quick, witty sentence."})
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio(pumpkin_audio_file)
    sleep(3)
    print("-------------- READY TO RUN --------------")

# =========== MAIN LOOP ===========
pir.when_motion = run_main

pause()