from openai import OpenAI
from utils import complete_task

client = OpenAI()


def validate(results):
    resp = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:research:AbAdrxXq",
        messages=[
            {"role": "system", "content": "Classify given results as correct or not"},
            {"role": "user", "content": results},
        ],
    )

    return resp.choices[0].message.content


correctIds = []
with open("tasks/research/verify.txt", "r") as file:
    for line in file:
        line = line.strip()

        id = line.split("=")[0]
        results = line.split("=")[1]

        validateResult = validate(line)

        if validateResult == "correct":
            correctIds.append(id)


complete_task("research", correctIds)
