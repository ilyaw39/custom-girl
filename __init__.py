import openai
import json


from nonebot.params import EventPlainText
from nonebot.rule import to_me
from nonebot import on_message

openai.api_key = "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"
MAX_HIST_LENGTH = 30
HISTORY_FILE = "/Users/ilyaw39/Developer/Chantelle/nonebot-client/src/plugins/custom-girl/prompt-hist.json"

matcher = on_message(rule=to_me())


@matcher.handle()
async def _(text: str = EventPlainText()):
    message = get_request(text=text)
    await matcher.send(message=message)


def get_resp(_prompts):
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=_prompts,
        presence_penalty=1.60,
        frequency_penalty=1.40,
        temperature=1.09)
    resp = resp['choices'][0]['message']['content']
    return resp


def get_request(text):
    with open(HISTORY_FILE, 'r',
              encoding='utf-8') as f:
        prompts = json.load(f)
    if len(prompts) > MAX_HIST_LENGTH:
        del prompts[1:6]
        with open(HISTORY_FILE, 'w',
                  encoding='utf-8') as f:
             json.dump(prompts, f)

    prompt = {"role": "user", "content": text}
    prompts.append(prompt)

    text = get_resp(prompts)
    resp = {"role": "assistant", "content": text}
    prompts.append(resp)

    with open(HISTORY_FILE, 'w',
              encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    return str(text)
