from openai import OpenAI
import requests
from utils import get_tasks_api_key, get_transcription, complete_task
import os
import re
import json

resp = requests.get("https://centrala.ag3nts.org/dane/arxiv-draft.html")
questions = requests.get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/arxiv.txt"
)

client = OpenAI()


def html_to_md(html):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                    Convert given HTML to markdown.

                    <RULES>
                    - Return only markdown text, nothing else
                    - Preserve all links
                    - Convert only body of html document
                    </RULES>
                """,
            },
            {"role": "user", "content": html},
        ],
    )

    return resp.choices[0].message.content


def get_answer(question, md, refers):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                    Answer given question based on provided markdown document.
                    Answer with JSON format. like this:
                {{
                    "put question id here": "krótka odpowiedź w 1 zdaniu",
                    "put question id here": "krótka odpowiedź w 1 zdaniu",
                    "put question id here": "krótka odpowiedź w 1 zdaniu",
                    "put question id here": "krótka odpowiedź w 1 zdaniu"
                }}

                    <RULES>
                    - Return only json object and nothing else.
                    - Answer cannot be placed in ```json``` block.
                    </RULES>

                    <DOCUMENT>
                    {md}
                    </DOCUMENT>

                    <REFERENCES>
                    {refers}
                    </REFERENCES>
                """,
            },
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content


def describe_audio(link):
    response = requests.get(link)

    if not os.path.exists("./tasks/arxiv/audio.mp3"):
        with open("./tasks/arxiv/audio.mp3", "wb") as f:
            f.write(response.content)

    return get_transcription("./tasks/arxiv/audio.mp3")


def describe_image(link):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You have perfect vision. Describe this image in detail. Look carefully as some images may not be exactly what they appear to be at first glance. Pay attention to any unusual or unexpected details.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://centrala.ag3nts.org/dane/" + link,
                        },
                    },
                ],
            }
        ],
    )

    return resp.choices[0].message.content


described_refs = []

with open("./tasks/arxiv/arxiv.md", "r", encoding="utf-8") as f:
    md = f.read()
    image_refs = re.findall(
        r"!\[(.*?)\](?:\n.*?)?\((.*?)\)", md, re.MULTILINE | re.DOTALL
    )
    link_refs = re.findall(r"\[(.*?)\]\((.*?)\)", md)

    refs = []
    for alt, path in image_refs:
        refs.append({"alt": alt.strip(), "path": path.strip(), "type": "image"})
    for text, path in link_refs:
        refs.append({"alt": text.strip(), "path": path.strip(), "type": "link"})

    for ref in refs:
        description = ""
        if ref["path"].endswith(".mp3"):
            description = describe_audio(
                "https://centrala.ag3nts.org/dane/" + ref["path"]
            )
        if ref["path"].endswith(".png"):
            description = describe_image(ref["path"])

        described_refs.append({**ref, "description": description})

    formatted_refs = "\n\n".join(
        [
            f"Reference {i+1}:\n"
            f"Type: {ref['type']}\n"
            f"Text/Alt: {ref['alt']}\n"
            f"Path: {ref['path']}\n"
            f"Description: {ref['description']}"
            for i, ref in enumerate(described_refs)
        ]
    )

    complete_task("arxiv", json.load(get_answer(questions.text, md, formatted_refs)))
