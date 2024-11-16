from requests import get
from utils import complete_task, get_tasks_api_key
from openai import OpenAI

description_resp = get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/robotid.json"
)

description_json = description_resp.json()

visual_description = OpenAI().chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": """
                Based on given information about robot, return its visual description.
                """,
        },
        {"role": "user", "content": description_json["description"]},
    ],
)

image_resp = OpenAI().images.generate(
    model="dall-e-3",
    prompt=visual_description.choices[0].message.content,
    n=1,
    size="1024x1024",
)


complete_task("robotid", image_resp.data[0].url)
