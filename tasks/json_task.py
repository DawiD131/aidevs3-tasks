import requests
from openai import OpenAI

from utils import complete_task, get_tasks_api_key


def get_answer(question):
    chat_completion = OpenAI().chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Answer questions as briefly and concisely as possible",
            },
            {"role": "user", "content": question},
        ],
    )

    return chat_completion.choices[0].message.content


resp = requests.get(
    "https://centrala.ag3nts.org/data/a6f443b2-e7fc-4f27-ac4e-c0ec9b3c370c/json.txt"
)

respData = resp.json()

answers = []
for x in respData["test-data"]:
    if "test" in x:
        answers.append(
            {
                **x,
                "answer": eval(x["question"]),
                "test": {**x["test"], "a": get_answer(x["test"]["q"])},
            }
        )
    else:
        answers.append({**x, "answer": eval(x["question"])})

respData["test-data"] = answers
respData["apikey"] = get_tasks_api_key()

complete_task("JSON", respData)
