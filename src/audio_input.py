# pulled from https://www.geeksforgeeks.org/create-a-voice-recorder-using-python/

import sounddevice as sd
sd.default.latency = 'low'
sd.default.device = 'USB PnP Sound Device'

from scipy.io.wavfile import write
import numpy as np

from time import perf_counter, sleep
from multiprocessing import Process, Queue

from speech_to_text import transcribe, transcribe_multiprocessing

# ===SETUP===

# Sampling frequency
freq = 44100
# Recording duration (s)
duration_short = 1
duration_long = 3

def get_audio_chunk(duration):
    print("started recording")
    # Start recorder with the given values of 
    # duration and sample frequency
    recording = sd.rec(int((duration) * freq), samplerate=freq, channels=1, blocking=True)
    # Record audio for the given number of seconds
    print("stopped recording")
    return recording    

def get_avg_amplitude(sample):
    return sum(np.absolute(sample))/len(sample)

def get_avg_amplitude_of_samples(num_trials):
    samples = []
    for i in range(num_trials):
        samples.append(get_audio_chunk(duration_long))
    
    amps = [get_avg_amplitude(sample) for sample in samples]
    avg_amplitude = sum(amps)/len(amps)
    return avg_amplitude

def check_speech_started(threshold, sample):
    minimum_syllable_speech_time_s = 0.2
    samples_per_syllable = int(freq * minimum_syllable_speech_time_s)
    
    i = 0
    while i+samples_per_syllable < len(sample):
        if get_avg_amplitude(sample[i:i+samples_per_syllable]) > threshold: return True
        i += samples_per_syllable
    
    return False

def check_speech_done(threshold, sample):
    return get_avg_amplitude(sample) < threshold

def check_speech_has_pause(threshold, sample):
    pause_speech_time_s = 0.4
    samples_per_pause = int(freq * pause_speech_time_s)
    
    i = 0
    while i+samples_per_pause < len(sample):
        if get_avg_amplitude(sample[i:i+samples_per_pause]) < threshold: return (True, i)
        i += samples_per_pause
    
    return (False, i)

# dummy function for testing GPT
def get_audio_input_test(number):
    responses = [
        "Oh sorry sir, I didn't know it was yours! How can you talk?",
        "Wow! That's super cool! So what's your favourite halloween movie? Mine is Ghostbusters!"
    ]
    return responses[number]

"""
Requirements:
1) start listening when kid starts speaking     ✅
2) stop listening when kid finishes speaking    ✅
3) transcribe on the fly                        ✅
"""

def get_audio_input(threshold_avg):
    print("##### RECORDING #####\n")
    recording = np.empty(0)
    filename = f"recordings/recording0.wav"
    
    started_speaking = False

    while True:
        sample = get_audio_chunk(duration_short)
        
        if not started_speaking:
            t1 = perf_counter()
            started_speaking = check_speech_started(threshold_avg, sample)
            t2 = perf_counter()
            print("checking for start of speech took ", round(t2-t1, 2), " seconds")
            if started_speaking: print("---LOG: started speaking")
        
        if started_speaking:
            recording = np.append(recording, sample)
        
        if started_speaking and check_speech_done(threshold_avg, sample):
            print("---LOG: end of speech")
            write(filename, freq, recording)

    full_transcription = transcribe(filename)
    print(full_transcription)
    return full_transcription

def get_audio_input_multiprocessing(threshold_avg):
    print("##### RECORDING #####\n")
    recording = np.empty(0)
    recordings_counter = 0
    
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

    started_speaking = False

    while True:
        t1 = perf_counter()
        sample = get_audio_chunk(duration_long)
        t2 = perf_counter()
        print("getting audio sample took ", round(t2-t1, 2), " seconds")
        
        if not started_speaking:
            t1 = perf_counter()
            started_speaking = check_speech_started(threshold_avg, sample)
            t2 = perf_counter()
            print("checking for start of speech took ", round(t2-t1, 2), " seconds")
            if started_speaking: print("---LOG: started speaking")
        
        if started_speaking:
            t1 = perf_counter()
            (has_pause, pause_index) = check_speech_has_pause(threshold_avg, sample)
            t2 = perf_counter()
            print("checking for pauses took ", round(t2-t1, 2), " seconds")
            # OpenAI whisper can't handle audio shorter than 0.1 seconds
            current_recording_duration = (len(recording) + len(sample[:pause_index])) / freq
            if has_pause and current_recording_duration > 0.1:
                print("---LOG: pause detected")
                # save up to the pause
                recording = np.append(recording, sample[:pause_index])
                # write current buffer to file
                filename = f"recordings/recording{recordings_counter}.wav"
                write(filename, freq, recording)
                # send job to transcribe current buffer
                jobs.put((recordings_counter, filename))
                print('---LOG: sending job ', recordings_counter)
                recordings_counter += 1
                # reset recording but include the speech from after the pause
                recording = np.array(sample[pause_index:])
            else:
                recording = np.append(recording, sample)
        
        if started_speaking and check_speech_done(threshold_avg, sample):
            print("---LOG: end of speech")
            current_recording_duration = len(recording) / freq
            if current_recording_duration > 0.1:
                # write leftover buffer to file and transcribe
                filename = f"recordings/recording{recordings_counter}.wav"
                write(filename, freq, recording)
                jobs.put((recordings_counter, filename))
            else:
                recordings_counter -= 1
            t1 = perf_counter()
            # inform processes to stop looking for jobs
            for i in range(MAX_PROCESSES):
                jobs.put(False)
            break

    # end processes
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
    
    for i in range(len(transcribed_files.keys())):
        full_transcription += transcribed_files[i]

    print(full_transcription)
    return full_transcription
    
    # Script
    """
    Felix is a very attractive individual.
    In his free time, he sleeps before four in the morning.
    That's why he's so hot. What a chad.
    """

# if __name__ == "__main__":
    # get_audio_input(0.03056035)