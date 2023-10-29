import os
from dotenv import load_dotenv
import openai

# testing
from time import perf_counter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

total_transcript = ""

for file in sorted(os.listdir('audio_out')):
    if file.split(".")[-1] != "wav": break
    t_start = perf_counter()
    audio_file = open(f"audio_out/{file}", "rb")
    transcript = openai.Audio.translate(model="whisper-1", file=audio_file, response_format="text")
    t_stop = perf_counter()
    print("Time taken (seconds): ", round(t_stop-t_start, 2))
    total_transcript += transcript

print(total_transcript)