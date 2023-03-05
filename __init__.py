import openai
import json
import math
import os


from nonebot.adapters import Message
from nonebot.matcher import Matcher

from nonebot.params import Arg, CommandArg, ArgPlainText

from nonebot import on_message
from nonebot.plugin import on_command
from nonebot.rule import to_me

openai.api_key = "" # Fill this with your key
MAX_HISTORY_LENGTH = 150

gpt = on_command("", to_me())

@gpt.handle()
async def handle_echo(message: Message = CommandArg()):
    message = str(message)
    text = get_request(text=message)
    await gpt.send(message=text)

def compute_weights(history, idx=-1):
    if "机器" in history[idx]["content"]:
        return 1.0

    if history[idx]["role"] == "user":
        if "!" in history[idx]["content"]:
            return 0.8
        elif "?" in history[idx]["content"]:
            return 0.6
        else:
            return 0.4

    if history[idx]["role"] == "system":
        if idx == 0:
            return 0.9
        else:
            return 0.1

    for i in range(idx - 1, -1, -1):
        if history[idx]["role"] == history[i]["role"]:
            continue

        sim_score = similarity_score(history[idx]["content"], history[i]["content"])
        decay = math.exp(-(idx - i))
        return decay * sim_score
    return 0.0


def similarity_score(str1, str2):
    overlap = set(str1.split()) & set(str2.split())
    return len(overlap) / (len(str1.split()) + len(str2.split()))


def get_history(history_file, create_if_not_exists=False):
    if not os.path.exists(history_file):
        if create_if_not_exists:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        else:
            raise FileNotFoundError(f"History file {history_file} not found.")
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    return history


def get_resp(prompts):
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=prompts,
        presence_penalty=1.90,
        frequency_penalty=1.55,
        temperature=1.05)
    resp = resp['choices'][0]['message']['content']
    return resp



with open('/Users/ilyaw39/Developer/Chantelle/Chantelle/src/plugins/custom-girl/prompt-hist.json', 'r', encoding='utf-8') as f:
    prompts = json.load(f)

with open('/Users/ilyaw39/Developer/Chantelle/Chantelle/src/plugins/custom-girl/prompt-hist-x.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

def get_request(text):
    prompt = {"role": "user", "content": text}
    prompts.append(prompt)

    weights = compute_weights(history)
    history.append({"role": "user", "content": prompts[-1]["content"], "weights": weights})

    text = get_resp(prompts)

    resp = {"role": "assistant", "content": text}
    prompts.append(resp)

    weights = compute_weights(history)
    history.append({"role": "assistant", "content": prompts[-1]["content"], "weights": weights})

    with open('/Users/ilyaw39/Developer/Chantelle/Chantelle/src/plugins/custom-girl/prompt-hist.json', 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    with open('/Users/ilyaw39/Developer/Chantelle/Chantelle/src/plugins/custom-girl/prompt-hist-x.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return str(text)


