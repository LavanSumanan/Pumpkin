# examples from https://platform.openai.com/docs/guides/gpt

import os
from dotenv import load_dotenv
import openai
from audio_input import get_audio_input_test

# testing
from time import perf_counter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# setup
system_prompt_message = "Pretend to be a funny jack o lantern. A kid is trying to steal from your candy bowl! Respond as jack o lantern would with a short, one sentence answer.'"
messages = [{"role": "system", "content": system_prompt_message}]

# pumpkin: response 1
t1_start = perf_counter()
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
t1_stop = perf_counter()
print("time taken (seconds): ", t1_stop-t1_start)
messages.append(response["choices"][0]["message"])
print("Pumpkin first says: ", messages[-1]["content"])
print("\n")

# kid: response 1
messages.append({"role": "user", "content": get_audio_input_test(0)})
print("Kid first replies: ", messages[-1]["content"])
print("\n")

# pumpkin: response 2
t2_start = perf_counter()
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
t2_stop = perf_counter()
print("time taken (seconds): ", t2_stop-t2_start)
messages.append(response["choices"][0]["message"])
print("Pumpkin then says: ", messages[-1]["content"])
print("\n")

# kid: response 2
messages.append({"role": "user", "content":get_audio_input_test(1)})
print("Kid secondly replies: ", messages[-1]["content"])
print("\n")

# pumpkin: ask question
messages.append({"role": "system", "content": "Now naturally shift the conversation to asking the kids 'Would you like a trick or a treat?'"})
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
messages.append(response["choices"][0]["message"])
print("Pumpkin asks final question: ", messages[-1]["content"])
print("\n")
