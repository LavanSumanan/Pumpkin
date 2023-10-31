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
    if highQualityTts:
        tts_high_quality(text, file)
    else:
        tts(text, file)

recording_path = '../recordings'
pumpkin_start_path = recording_path + '/pumpkin_start'
pumpkin_response_path = recording_path + '/pumpkin_response'
pumpkin_trick_path = recording_path + '/pumpkin_trick'
user_path = recording_path + '/user'
warn_path = recording_path + '/warn'

pumpkin_start_file_index = int(sorted(os.listdir(pumpkin_start_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_start_path)) else 0
pumpkin_trick_file_index = int(sorted(os.listdir(pumpkin_trick_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_trick_path)) else 0

def get_pumpkin_file_name(path=pumpkin_response_path, random=False):
    if path == pumpkin_response_path:
        return f'{pumpkin_response_path}/pumpkin.{ttsExtension}'
    
    global pumpkin_start_file_index
    global pumpkin_trick_file_index
    
    index_map = {
        pumpkin_start_path: pumpkin_start_file_index,
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

def play_audio_io(filename):
    visible_led.on()
    play_audio(filename)
    visible_led.off()

# =========== INITIALIZATION ===========
def reset_io():
    red_led.off()
    green_led.off()
    visible_led.on()
    pir.wait_for_no_motion()
reset_io()

def reset_user_recordings():
    for filename in os.listdir(user_path):
        if os.path.isfile(os.path.join(user_path, filename)):
            os.remove(os.path.join(user_path, filename))
reset_user_recordings()

def run_main():
    print("-------------- START --------------")
    # reset pumpkin gpt's context
    messages = reset_pumpkin_gpt()
    pumpkin_audio_file = None
    
    # startle person by talking for the first time
    if pumpkin_start_file_index < 10:
        pumpkin_audio_file = get_pumpkin_file_name(pumpkin_start_path)
        tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    else:
        pumpkin_audio_file = get_pumpkin_file_name(pumpkin_start_path, random=True)
    print('pumpkin start audio file name: ', pumpkin_audio_file)
    
    pumpkin_audio_file = get_pumpkin_file_name()
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio_io(pumpkin_audio_file)
    
    # listen to person's response and add to pumpkin gpt's context
    messages.append({"role": "user", "content": get_audio_io()})
    
    # pumpkin gpt responds to person
    messages.append({"role": "system", "content": "Respond to the kid's message in a short, fun sentence, and then ask the kid what their favourite part of Halloween is."})
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio_io(pumpkin_audio_file)
    
    # listen to person again
    messages.append({"role": "user", "content": get_audio_io()})
    
    # pumpkin gpt responds and asks "trick or treat"
    messages.append({"role": "system", "content": "Respond to the kid in a short, fun sentence, and then naturally shift the conversation to asking the kids 'Would you like a trick or a treat?'"})
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio_io(pumpkin_audio_file)
    response = get_audio_io().lower().strip()
    # transcription sometimes mistakes "treat" for "tree"
    if "treat" in response or "tree" in response:
        play_audio_io(f'{recording_path}/dispense.{ttsExtension}')
        print("Dispensing candy!!")
        for i in range(4):
            servo.value = SERVO_MIN
            sleep(0.7)
            servo.value = SERVO_MAX
            sleep(0.7)
        servo.value = 0
    else:
        if pumpkin_trick_file_index < 10:
            messages.append({"role": "system", "content": "Create a short, one sentence joke about Halloween."})
            pumpkin_audio_file = get_pumpkin_file_name(pumpkin_trick_path)
            tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
        else:
            pumpkin_audio_file = get_pumpkin_file_name(pumpkin_trick_path, random=True)
        play_audio_io(pumpkin_audio_file)

    print("-------------- END --------------")
    # wait for people to leave
    pumpkin_audio_file = get_pumpkin_file_name()
    messages.append({"role": "system", "content": "Now tell the kid to shoo with a quick, witty sentence."})
    tts_call(get_pumpkin_response(messages), pumpkin_audio_file)
    play_audio_io(pumpkin_audio_file)
    visible_led.on()
    sleep(5)
    print("-------------- READY TO RUN --------------")

# =========== MAIN LOOP ===========
pir.when_motion = run_main

pause()