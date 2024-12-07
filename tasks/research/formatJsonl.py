result = ""
with open("tasks/research/correct.txt", "r") as file:
    for line in file:
        line = line.strip()

        result += f"""{{"messages": [ {{"role": "system", "content": "Classify given results as correct or not"}}, {{"role": "user", "content": "{line}"}}, {{"role": "assistant", "content": "correct"}} ]}}\n"""

with open("tasks/research/incorrect.txt", "r") as file:
    for line in file:
        line = line.strip()
        result += f"""{{"messages": [ {{"role": "system", "content": "Classify given results as correct or not"}}, {{"role": "user", "content": "{line}"}}, {{"role": "assistant", "content": "incorrect"}} ]}}\n"""


with open("tasks/research/result.jsonl", "w") as f:
    f.write(result)
