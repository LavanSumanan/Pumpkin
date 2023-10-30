# pulled from https://www.geeksforgeeks.org/create-a-voice-recorder-using-python/

import sounddevice as sd
sd.default.latency = 'low'
sd.default.device = 'USB PnP Sound Device'

from scipy.io.wavfile import write
import numpy as np

from time import perf_counter, sleep
from multiprocessing import Process, Queue

from speech_to_text import transcribe

# ===SETUP===

# Sampling frequency
freq = 44100
# Recording duration (s)
duration_s = 3

def get_audio_chunk():
    print("started recording")
    # Start recorder with the given values of 
    # duration and sample frequency
    recording = sd.rec(int((duration_s) * freq), samplerate=freq, channels=1, blocking=True)
    # Record audio for the given number of seconds
    print("stopped recording")
    return recording    

def get_avg_amplitude(chunk_array):
    return sum(np.absolute(chunk_array))/len(chunk_array)

def check_speech_started(threshold, chunk_array):
    minimum_syllable_speech_time_s = 0.2
    samples_per_syllable = int(freq * minimum_syllable_speech_time_s)
    
    i = 0
    while i+samples_per_syllable < len(chunk_array):
        if get_avg_amplitude(chunk_array[i:i+samples_per_syllable]) > threshold: return True
        i += samples_per_syllable
    
    return False

def check_speech_done(threshold, chunk_array):
    return get_avg_amplitude(chunk_array) < threshold

def get_avg_amplitude_of_samples(NUM_TRIALS):
    samples = []
    for i in range(NUM_TRIALS):
        samples.append(get_audio_chunk())
    
    amps = [get_avg_amplitude(sample) for sample in samples]
    avg_amplitude = sum(amps)/len(amps)
    return avg_amplitude

# dummy function for testing GPT
def get_audio_input_test(number):
    responses = [
        "Oh sorry sir, I didn't know it was yours! How can you talk?",
        "Wow! That's super cool! So what's your favourite halloween movie? Mine is Ghostbusters!"
    ]
    return responses[number]

# TODO
"""
check_for_pause function that goes through current sample,
sees if there's a time interval of length n (determine n, guessing like 800ms or smth)
in which the average amplitude falls below threshold.
if so, combine the current recording list into one array and ship it off to another thread to
start transcribing (w/ whisper), then wipe current recording list and keep recording in this thread
"""

"""
Requirements:
1) start listening when kid starts speaking     ✅
2) stop listening when kid finishes speaking    ✅
3) transcribe on the fly                        x
"""

def main(threshold_avg):
    print("##### RECORDING #####\n")
    recording = np.empty(0)
    
    # transcriptions are tuples of shape (transcription: string, index: int)
    transcriptions = Queue()
    MAX_PROCESSES = 3
    transcribers = [Process(target=transcribe, args=()) for i in range(MAX_PROCESSES)]
    transcribed_files = set()

    startedSpeaking = False

    while True:
        t1 = perf_counter()
        sample = get_audio_chunk()
        t2 = perf_counter()
        print("getting audio sample took ", round(t2-t1, 2), " seconds")
        
        if not startedSpeaking:
            startedSpeaking = check_speech_started(threshold_avg, sample)
        
        if startedSpeaking:
            recording = np.append(recording, sample)
            # whisper transcribing stuff
        
        if startedSpeaking and check_speech_done(threshold_avg, sample):
            break

    # for i, sample in enumerate(recording):
    write(f"audio_out/recording0.wav", freq, recording)

    # Script
    """
    Felix is a very attractive individual.
    In his free time, he sleeps before four in the morning.
    That's why he's so hot. What a chad.
    """

if __name__ == "__main__":
    main(0.03056035)