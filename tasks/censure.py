import requests
from openai import OpenAI

from utils import complete_task, get_tasks_api_key


resp = requests.get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/cenzura.txt"
)

print(resp.text)


def get_answer(question):
    chat_completion = OpenAI().chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                    Mask potential sensitive words in the text to CENZURA

                    <RULES>
                    - You can't change original text
                    - mask only words that are potentially sensitive like names, surnames, age, places, etc.
                    - you can't remove any words from the text
                    - Replace all sensitive data (first + last name, street name + number, city, person's age) with the word CENZURA
                    - Preserve all periods, commas, spaces, etc. You must not edit the text structure
                    </RULES>
                """,
            },
            {"role": "user", "content": question},
        ],
    )

    return chat_completion.choices[0].message.content


complete_task("CENZURA", get_answer(resp.text))
