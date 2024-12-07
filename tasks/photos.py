import json
from openai import OpenAI
from .utils import get_tasks_api_key, complete_task
from requests import post

client = OpenAI()


def ask(answer):
    resp = post(
        "https://centrala.ag3nts.org/report",
        json={
            "task": "photos",
            "apikey": get_tasks_api_key(),
            "answer": answer,
        },
    )
    return resp.json()


def extract_photos_urls(message):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                Extract all photo URLs from the message, and return it as json array
                 
                BASE_URL = https://centrala.ag3nts.org/dane/barbara/
                <RULES>
                - Return only URLs, nothing else
                - Return valid JSON array
                - JSON couldn't be in ```JSON``` block
                </RULES>
                """,
            },
            {"role": "user", "content": message},
        ],
    )
    return resp.choices[0].message.content


def process_photo(command, image_name):
    resp = ask(command + " " + image_name)
    return resp["message"]


def select_tool(imge_url, image_name):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": imge_url, "detail": "high"},
                    },
                    {
                        "type": "text",
                        "text": f"Image name = {image_name}",
                    },
                ],
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "selected_tool",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "object",
                            "properties": {
                                "tool_name": {
                                    "type": "string",
                                    "description": "Name of the tool to use from the list: DARKEN (darken image if its too bright), REPAIR (repair image if its damaged), BRIGHTEN (brighten image if its too dark), NOTHING (if image is fine)",
                                },
                                "image_name": {
                                    "type": "string",
                                    "description": "Name of the image to use",
                                },
                            },
                            "required": ["tool_name", "image_name"],
                            "additionalProperties": False,
                        }
                    },
                    "required": ["tool"],
                    "additionalProperties": False,
                },
            },
        },
    )
    return resp.choices[0].message.content


message = ask("START")["message"]

image_urls = json.loads(extract_photos_urls(message))

tools = {
    "DARKEN": lambda name: process_photo("DARKEN", name),
    "REPAIR": lambda name: process_photo("REPAIR", name),
    "BRIGHTEN": lambda name: process_photo("BRIGHTEN", name),
}

processed_photos = []
for image_url in image_urls:
    tool_response = select_tool(image_url, image_url.rstrip("/").split("/")[-1])
    tool = json.loads(tool_response)
    tool_name = tool["tool"]["tool_name"]

    if tool_name == "NOTHING":
        continue
    image_name = tool["tool"]["image_name"]
    tool_response = tools[tool_name](image_name)
    processed_photos.append(json.loads(extract_photos_urls(tool_response))[0])


processed_photos = [
    "https://centrala.ag3nts.org/dane/barbara/IMG_559_FGR4.PNG",
    "https://centrala.ag3nts.org/dane/barbara/IMG_1410_FXER.PNG",
    "https://centrala.ag3nts.org/dane/barbara/IMG_1443_FT12.PNG",
]


def describe_person_on_photos(photos_urls):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    *(
                        {
                            "type": "text",
                            "text": f"""Generate general description of the person on the photos in details
                            
                            focus on these aspects:
                            - hair color
                            - eyes color
                            - clothing
                            - specific features
                            - any other distinguishing characteristics

                            Generate description in Polish for all images in one response
                            """,
                        },
                        *(
                            {
                                "type": "image_url",
                                "image_url": {"url": url, "detail": "high"},
                            }
                            for url in photos_urls
                        ),
                    )
                ],
            }
        ],
    )
    return resp.choices[0].message.content


complete_task("photos", describe_person_on_photos(processed_photos))
