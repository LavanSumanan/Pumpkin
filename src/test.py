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

# import os
# pumpkin_start_file_index = sorted(os.listdir('../recordings/pumpkin_start'), reverse=True)[0][0] if sorted(os.listdir('../recordings/pumpkin_start')) else 0
# print(pumpkin_start_file_index)