from gtts import gTTS
from resemble import Resemble
from dotenv import load_dotenv
import time
import os
from urllib.request import urlretrieve
from playsound import playsound

load_dotenv()
LANGUAGE = 'en'

######### RESEMBLE CREDS
Resemble.api_key(os.getenv("RESEMBLE_API_KEY"))
project_uuid = 'ae8c9c27'
voice_uuid = '48d7ed16'
##########


def tts(text, output_file):
    """NOTE: output format is .mp3"""
    t1 = time.perf_counter()
    myobj = gTTS(text=text, lang=LANGUAGE, slow=False) 
    myobj.save("hello.mp3") 
    t2 = time.perf_counter()
    print(f"TTS low quality time taken:{t2 - t1}")


def tts_high_quality(text, output_file):
    """NOTE: output format is .wav"""
    t1 = time.perf_counter()
    response = Resemble.v2.clips.create_sync(
    project_uuid,
    voice_uuid,
    text,
    title=None,
    sample_rate=22050,
    output_format=None,
    precision=None,
    include_timestamps=None,
    is_public=None,
    is_archived=None,
    raw=None
    )

    try:
        clip_src = response['item']['audio_src']
        urlretrieve(clip_src, output_file)
        t2 = time.perf_counter()
        print(f"TTS high quality time taken:{t2 - t1}")
    except:
        print("ERROR creating high quality TTS clip")
        print(response)

# EXAMPLE CALL
# tts_high_quality("Felix is a very attractive individual."
#     "In his free time, he sleeps before four in the morning."
#     "That's why he's so smexy wexy. What a chad.", "hello.wav")

def play_audio(filename):
    playsound(filename)
    print(f'Playing file {filename}')