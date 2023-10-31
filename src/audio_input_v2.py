import queue
import sys
import os

import sounddevice as sd
import soundfile as sf
import numpy as np
import time

from collections import deque
from dotenv import load_dotenv
load_dotenv()



sd.default.latency = 'low'
sd.default.device = os.getenv("MIC")
SAMPLE_RATE = 44100
CHANNELS = 1
OUTPUT_DIR = "output"
SHORT_LENGTH = int(0.4 * SAMPLE_RATE)
LONG_LENGTH = int(5.0 * SAMPLE_RATE)
MIN_LENGTH = int(1.0 * SAMPLE_RATE)
TINY_LENGTH = int(0.2 * SAMPLE_RATE)



def reset(_threshold):
    global q
    global recording_index
    global desired_recording_index
    global short_window
    global long_window
    global short_sum
    global long_sum
    global short_threshold
    global long_threshold
    global STATUS_terminate
    global STATUS_started
    global sample_index
    global started_index
    global chunk_start_index

    global tiny_window
    global tiny_sum
    global tiny_threshold

    q = queue.Queue()
    recording_index = 0
    desired_recording_index = 0
    tiny_window = deque()
    short_window = deque()
    long_window = deque()
    tiny_sum = 0.0
    short_sum = 0.0
    long_sum = 0.0
    tiny_threshold = _threshold * TINY_LENGTH
    short_threshold = _threshold * SHORT_LENGTH
    long_threshold = _threshold * LONG_LENGTH
    STATUS_started = False
    STATUS_terminate = False
    sample_index = 0
    started_index = 0
    chunk_start_index = 0


def callback(indata, frames, _time, status):
    global short_sum
    global long_sum
    global STATUS_terminate
    global STATUS_started
    global sample_index
    global started_index
    global desired_recording_index
    global chunk_start_index
    global tiny_sum


    if status:
        print(status, file=sys.stderr)
    if(STATUS_started):
        q.put(indata.copy())

    # update the deques
    for i, [x] in enumerate(indata):
        sample_index += 1
        short_sum += abs(x)
        long_sum += abs(x)
        tiny_sum += abs(x)
        long_window.append(x)
        short_window.append(x)
        tiny_window.append(x)

        speech_now = False
        if len(tiny_window) > TINY_LENGTH:
            tiny_sum -= abs(tiny_window.popleft())
            if tiny_sum > tiny_threshold:
                #there is speech at this instant
                speech_now = True

        if len(short_window) > SHORT_LENGTH:
            short_sum -= abs(short_window.popleft())
            if short_sum < short_threshold:
                if not speech_now and STATUS_started and sample_index > MIN_LENGTH + chunk_start_index:
                    # gap in speech
                    desired_recording_index = max(desired_recording_index, recording_index + 1)
                    chunk_start_index = sample_index
            else:
                # start speech
                if not STATUS_started:
                    STATUS_started = True
                    started_index = sample_index
                    q.put([[a] for a in short_window])
                    print("STARTED SPEECH")

        if len(long_window) > LONG_LENGTH:
            long_sum -= abs(long_window.popleft())
            if not speech_now and STATUS_started and long_sum < long_threshold and sample_index > MIN_LENGTH + started_index:
                # end of speech
                STATUS_terminate = True

def get_audio():
    global recording_index
    global desired_recording_index

    with sd.InputStream(samplerate=SAMPLE_RATE, device=sd.default.device, channels=CHANNELS, callback=callback):
        print("RECORDING...")
        while not STATUS_terminate:
            filename = f"{OUTPUT_DIR}/rec{recording_index}.wav"
            with sf.SoundFile(filename, mode='x', samplerate=SAMPLE_RATE, channels=CHANNELS, subtype="PCM_24") as file:
                print(f"Starting recording {recording_index}")
                while True:
                    file.write(q.get())
                    if desired_recording_index > recording_index:
                        #TODO multiprocess
                        break
                    if STATUS_terminate:
                        break
            recording_index += 1

reset(0.01)
get_audio()