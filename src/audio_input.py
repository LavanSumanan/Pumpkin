# pulled from https://www.geeksforgeeks.org/create-a-voice-recorder-using-python/

import soundfile as sf
sd.default.latency = 'low'
import sounddevice as sd
import tempfile
from scipy.io.wavfile import write
import numpy as np

from time import perf_counter, sleep

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

def geometric_mean(*args):
    mean = 1
    n = 0
    for arg in args:
        n += 1
        mean *= arg
    return mean**(1/n)

# determines THRESHOLD_AMPLITUDE to adjust to workplace/mic noise level
def calibrate_threshold():
    # list of nps
    talking = []
    NUM_TRIALS = 3
    for i in range(NUM_TRIALS):
        talking.append(get_audio_chunk())
    
    talking_amps = [get_avg_amplitude(sample) for sample in talking]
    talking_avg_amplitude = sum(talking_amps)/len(talking_amps)
    print("Talking avg amp: ", talking_avg_amplitude)
    sleep(2)
    
    # list of nps
    silence = []
    for i in range(NUM_TRIALS):
        silence.append(get_audio_chunk())
    
    silence_amps = [get_avg_amplitude(sample) for sample in silence]
    silence_avg_amplitude = sum(silence_amps)/len(silence_amps)
    print("Silence avg amp: ", silence_avg_amplitude)
    sleep(2)

    return geometric_mean(talking_avg_amplitude, silence_avg_amplitude)

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

def main():
    print("##### CALIBRATION #####\n")
    # THRESHOLD_AVG = calibrate_threshold()
    THRESHOLD_AVG = 0.01335005
    print("THRESHOLD_AVG SET TO ", THRESHOLD_AVG)


    sleep(1) # replace with waiting for motion to be detected
    
    print("##### RECORDING #####\n")
    recording = np.empty(0)
    with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,channels=args.channels, subtype=args.subtype) as file:
        with sd.InputStream(samplerate=args.samplerate, device=args.device,channels=args.channels, callback=callback):
            while True:
                file.write(q.get())

    startedSpeaking = False

    while True:
        t1 = perf_counter()
        sample = get_audio_chunk()
        t2 = perf_counter()
        print("getting audio sample took ", round(t2-t1, 2), " seconds")
        
        if not startedSpeaking:
            startedSpeaking = check_speech_started(THRESHOLD_AVG, sample)
        
        if startedSpeaking:
            recording = np.append(recording, sample)
            # whisper transcribing stuff
        
        if startedSpeaking and check_speech_done(THRESHOLD_AVG, sample):
            break

    # for i, sample in enumerate(recording):
    write(f"audio_out/recording0.wav", freq, recording)

    # Script
    """
    Felix is a very attractive individual.
    In his free time, he sleeps before four in the morning.
    That's why he's not single. What a chad.
    """

if __name__ == "__main__":
    main()