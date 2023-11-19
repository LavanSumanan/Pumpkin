# import os
#     for file in sorted(os.listdir('audio_out')):
#         if file.split(".")[-1] != "wav": break

# import numpy as np
# from multiprocessing import Process, Queue, current_process
# from time import sleep

# def test(a, b):
#     thread = current_process().name
#     while True:
#         x = a.get()
#         if not x:
#             break
#         print(thread, " started working on " + x)
#         sleep(5)
#         b.put(thread)
#     print(thread, " exited while loop")

# a = Queue()
# b = Queue()

# processes = [Process(target=test, args=(a,b)) for i in range(2)]

# for process in processes:
#     process.start()

# a.put("first task")
# sleep(2)
# a.put("second task")
# # done assigning tasks, input Falses
# a.put(False)
# a.put(False)
# print(b.get()) # process 1
# print(b.get()) # process 2

# for process in processes:
#     process.join()

# from text_to_speech import tts, tts_high_quality, play_audio
# file_out = 'fun.mp3'
# tts('Testing 1 2 3.', file_out)

# from gpiozero import LED, Button, MotionSensor, Servo
# from signal import pause

# from time import sleep

# talk_led = LED(22)
# silence_led = LED(17)
# button = Button(27, hold_time=1)
# pir = MotionSensor(18)
# red_led = LED(22)
# green_led = LED(17)
# visible_led = LED(23)

# servo = Servo(18)

# for i in range(4):
#     servo.value = -1
#     sleep(0.7)
#     servo.value = 1
#     sleep(0.7)
# servo.value = 0

# visible_led.off()
# green_led.on()
# red_led.on()

# talk_led.off()
# pir.wait_for_no_motion()
# silence_led.off()

# def fake_calibration():
#     print("begin calibrating")
#     talk_led.on()
#     sleep(4)
#     talk_led.off()
#     print("end calibrating")

# button.when_held = fake_calibration

# def fake_trigger_program():
#     print("program starts")
#     play_audio(file_out)
#     sleep(3)
#     print("done program")

# pir.when_motion = fake_trigger_program
# pir.when_no_motion = lambda _: print("motion no longer detected")

# pause()

# highQualityTts = True
# ttsExtension = "wav" if highQualityTts else "mp3"
# print(ttsExtension)

# import os

# highQualityTts = False # flip flag to use high vs. low quality TTS
# ttsExtension = 'wav' if highQualityTts else 'mp3'
# recording_path = '../recordings'
# pumpkin_start_path = recording_path + '/pumpkin_start'
# pumpkin_start_file_index = int(sorted(os.listdir(pumpkin_start_path), reverse=True)[0][0]) if sorted(os.listdir(pumpkin_start_path)) else 0
# print(pumpkin_start_file_index)

# def get_pumpkin_start_file():
#     global pumpkin_start_file_index
#     filename = f'{pumpkin_start_path}/{pumpkin_start_file_index}pumpkin.{ttsExtension}'
#     pumpkin_start_file_index += 1
#     return filename

# print(get_pumpkin_start_file())
# print(get_pumpkin_start_file())

# import os

# highQualityTts = False # flip flag to use high vs. low quality TTS
# ttsExtension = 'wav' if highQualityTts else 'mp3'

# recording_path = '../recordings'
# pumpkin_start_path = recording_path + '/pumpkin_start'
# pumpkin_response_path = recording_path + '/pumpkin_response'
# pumpkin_trick_path = recording_path + '/pumpkin_trick'
# user_path = recording_path + '/user'

# pumpkin_start_file_index = sorted(os.listdir(pumpkin_start_path), reverse=True)[0][0] if sorted(os.listdir(pumpkin_start_path)) else 0
# pumpkin_trick_file_index = sorted(os.listdir(pumpkin_trick_path), reverse=True)[0][0] if sorted(os.listdir(pumpkin_trick_path)) else 0

# def get_pumpkin_file_name(start=False, random=False, trick=False):
#     if not start: return f'{pumpkin_response_path}/pumpkin.{ttsExtension}'
    
#     global pumpkin_start_file_index
#     global pumpkin_trick_file_index
#     path = pumpkin_start_path if not trick else pumpkin_trick_path
#     index = pumpkin_start_file_index if not trick else pumpkin_trick_file_index
    
#     if random: return f'{path}/{randint(0,9)}pumpkin.{ttsExtension}'
    
#     filename = f'{path}/{index}pumpkin.{ttsExtension}'
#     index += 1
#     return filename

# get_pumpkin_file_name(True)
# get_pumpkin_file_name(False)
# get_pumpkin_file_name(True)
# get_pumpkin_file_name(trick=True)
# get_pumpkin_file_name(trick=True)

# from text_to_speech import tts, play_audio
# tts('Calibration complete', '../recordings/warn/complete.mp3')
# tts('Record background noise when the light turns on', '../recordings/warn/silent.mp3')
# play_audio('../recordings/warn/silent.mp3')

# from gpiozero import Servo
# from time import sleep

# servo = Servo(18)
# servo.value = 1
# sleep(2)
# servo.value = -1

# try:
#     while True:
#         servo.value = -1
#         sleep(2)
#         servo.value = 1
#         sleep(2)
# except KeyboardInterrupt:
#     print("Program stopped")

# from text_to_speech import tts, tts_high_quality, play_audio
# tts('Fine, you can have just a bit of my candy!', "../recordings/dispense.mp3")
# tts_high_quality('Fine, you can have just a bit of my candy!', "../recordings/dispense.wav")
# play_audio("../recordings/dispense.mp3")
# play_audio("../recordings/dispense.wav")

# from audio_input_v2 import reset, get_audio
# reset(0.07)
# print(get_audio())

from speech_to_text import transcribe
from text_to_speech import tts_high_quality
from gpt import get_pumpkin_response, reset_pumpkin_gpt

for i in range(5,11):
    start_file = f"../recordings/pumpkin_start/{i}pumpkin.mp3"
    print(start_file)
    tts_high_quality(transcribe(start_file), f"../recordings/pumpkin_start/{i}pumpkin.wav")
    messages = reset_pumpkin_gpt()
    messages.append({"role": "system", "content": "Tell the kid to shoo with a quick, witty sentence."})
    stop_script = get_pumpkin_response(messages)
    tts_high_quality(stop_script, f"../recordings/pumpkin_stop/{i}pumpkin.wav")

# full_transcription = ""

# transcribed_files = {
#     0: "Hello world. ",
#     1: "This is cool. ",
#     2: "you",
#     3: " ",
#     4: "Pog. ",
#     5: "You",
#     6: "Thanks for watching!",
#     7: "You are so cool. No, you are."
# }

# for _, val in transcribed_files.items():
#     if val not in ["you", "You", "Thanks for watching!"]:
#         full_transcription += val

# print(full_transcription)

# from gpt import reset_pumpkin_gpt, get_pumpkin_response
# from text_to_speech import tts, play_audio
# messages = reset_pumpkin_gpt()
# messages.append({"role": "user", "content": "How can you talk?"})
# trigger_pumpkin_ask_question(messages)
# print(messages)
# response = get_pumpkin_response(messages)
# print(response)
# play_audio('../recordings/test/pumpkinquestion.mp3')