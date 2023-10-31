# examples from https://platform.openai.com/docs/guides/gpt

import os
from dotenv import load_dotenv
import openai

# testing
from time import perf_counter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def reset_pumpkin_gpt():
    system_prompt_message = "Pretend to be a funny jack o lantern. A kid is trying to steal from your candy bowl! Respond as jack o lantern would with a short, one sentence answer. Then ask the kid what their name is.'"
    return [{"role": "system", "content": system_prompt_message}]

def get_pumpkin_response(messages):
    t1 = perf_counter()
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    t2 = perf_counter()
    print("GPT response time:", t2-t1)
    messages.append(response["choices"][0]["message"])
    return messages[-1]["content"]

def test_pumpkin_gpt():
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
    messages.append({"role": "user", "content": "Oh sorry! How can you talk?"})
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
    messages.append({"role": "user", "content":" Wow! What's your favourite movie?"})
    print("Kid secondly replies: ", messages[-1]["content"])
    print("\n")

    # pumpkin: ask question
    messages.append({"role": "system", "content": "Now naturally shift the conversation to asking the kids 'Would you like a trick or a treat?'"})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    messages.append(response["choices"][0]["message"])
    print("Pumpkin asks final question: ", messages[-1]["content"])
    print("\n")
