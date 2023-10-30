from gtts import gTTS
from resemble import Resemble
from dotenv import load_dotenv
from time import perf_counter
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
    t1 = perf_counter()
    myobj = gTTS(text=text, lang=LANGUAGE, slow=False) 
    myobj.save("hello.mp3") 
    t2 = perf_counter()
    print(f"TTS low quality time taken:{t2 - t1}")


def tts_high_quality(text, output_file):
    """NOTE: output format is .wav"""
    t1 = perf_counter()
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
        t2 = perf_counter()
        print(f"TTS high quality time taken:{t2 - t1}")
    except:
        print("ERROR creating high quality TTS clip")
        print(response)

def play_audio(filename):
    playsound(filename)
    print(f'Playing file {filename}')

# EXAMPLE CALL
#tts("I fear no man. But Lovin. When I first saw that hunk of a man, I immediately felt shivers down my spine.", "hello.mp3")
#play_audio("hello.mp3")