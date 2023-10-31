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

# from gpiozero import LED, Button, MotionSensor
# from signal import pause

# from time import sleep

# talk_led = LED(22)
# silence_led = LED(17)
# button = Button(27, hold_time=1)
# pir = MotionSensor(18)

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

import os

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
# tts('Talk as a user would when the light turns on', '../recordings/warn/talk.mp3')
# play_audio('../recordings/warn/talk.mp3')
# tts('Record background noise when the light turns on', '../recordings/warn/silent.mp3')
# play_audio('../recordings/warn/silent.mp3')