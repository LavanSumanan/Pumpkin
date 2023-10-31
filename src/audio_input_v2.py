import queue
import sys
import os

import sounddevice as sd
import soundfile as sf
from time import perf_counter

from multiprocessing import Process, Queue

from collections import deque
from dotenv import load_dotenv
load_dotenv()

from speech_to_text import transcribe, transcribe_multiprocessing



sd.default.latency = 'low'
sd.default.device = os.getenv("MIC")
SAMPLE_RATE = 44100
CHANNELS = 1
OUTPUT_DIR = "../recordings/user"
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
        print("status: ", status, file=sys.stderr)
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

    # raspberry pi 4 has 4 core CPU, one core is running this script
    MAX_PROCESSES = 3
    # jobs are tuples of type (index: int, filename: string)
        # insert False 3 times when recording ends (one to end each process)
    jobs = Queue()
    # results are tuples of type (index: int, transcription: string)
    results = Queue()
    processes = [Process(target=transcribe_multiprocessing, args=(jobs, results)) for i in range(MAX_PROCESSES)]
    for process in processes:
        process.start()

    with sd.InputStream(samplerate=SAMPLE_RATE, device=sd.default.device, channels=CHANNELS, callback=callback):
        print("RECORDING...")
        while not STATUS_terminate:
            filename = f"{OUTPUT_DIR}/{recording_index}.wav"
            with sf.SoundFile(filename, mode='x', samplerate=SAMPLE_RATE, channels=CHANNELS, subtype="PCM_24") as file:
                print(f"Starting recording {recording_index}")
                while True:
                    file.write(q.get())
                    if desired_recording_index > recording_index:
                        jobs.put((recording_index, filename))
                        break
                    if STATUS_terminate:
                        jobs.put((recording_index, filename))
                        break
            recording_index += 1
        t1 = perf_counter()

    #terminate jobs
    for i in range(MAX_PROCESSES):
        jobs.put(False)
    for process in processes:
        process.join()
    t2 = perf_counter()
    print("from end of speech to final transcription took ", round(t2-t1, 2), " seconds")

    # files are a hashmap of type [index: int]: transcription: string
    transcribed_files = {}
    while not results.empty():
        (index, transcription) = results.get()
        transcribed_files[index] = transcription
 
    full_transcription = ""
    
    for i in range(len(transcribed_files.keys()) - 1):
        if transcribed_files[i] not in ["you", "You", "Thanks for watching!"]:
            full_transcription += transcribed_files[i]

    print(full_transcription)
    for filename in os.listdir(OUTPUT_DIR):
        if os.path.isfile(os.path.join(OUTPUT_DIR, filename)):
            os.remove(os.path.join(OUTPUT_DIR, filename))
    
    
    
    return full_transcription

## usage
if __name__ == '__main__':   
    reset(0.01)   # reset is MANDATORY
    get_audio()