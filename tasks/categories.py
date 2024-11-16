import base64

from openai import OpenAI
import os
import json
from utils import complete_task, get_tasks_api_key


client = OpenAI()


def categorize_content(content):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                    <thinking>
                    Categorize given content into one of the following categories:
                    - people (if provided content contains information about people)
                    - hardware (if provided content contains information about hardware failure or specific devices. Software not included here)
                    - other (if provided content doesn't contain information about people or hardware)

                    <RULES>
                    - Return only category name and nothing else.
                    - If content is about people in general, return "other"
                    </RULES>
                """,
            },
            {"role": "user", "content": content},
        ],
    )

    return response.choices[0].message.content


def get_transcription(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcription.text


def describe_image(image):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You have perfect vision and your task is to extract text from image",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",
                            "detail": "high",
                        },
                    }
                ],
            },
        ],
    )

    return response.choices[0].message.content


def load_factory_files(extension):
    factory_files = []
    directory = "./tasks/pliki_z_fabryki/"

    for filename in os.listdir(directory):
        if filename.endswith(extension):
            file_path = os.path.join(directory, filename)
            if extension == ".mp3":
                factory_files.append(
                    {"filename": filename, "content": open(file_path, "rb")}
                )
            else:
                mode = "r" if extension == ".txt" else "rb"
                with open(file_path, mode) as file:
                    content = file.read()
                    if extension == ".png":
                        content = base64.b64encode(content).decode("utf-8")
                    factory_files.append({"filename": filename, "content": content})

    return factory_files


factory_txt_files = load_factory_files(".txt")
factory_mp3_files = load_factory_files(".mp3")
factory_png_files = load_factory_files(".png")


categorized_files = []

for file in factory_txt_files:
    categorized_files.append(
        {"filename": file["filename"], "category": categorize_content(file["content"])}
    )

for file in factory_png_files:
    img_desc = describe_image(file["content"])
    categorized_files.append(
        {"filename": file["filename"], "category": categorize_content(img_desc)}
    )

for file in factory_mp3_files:
    transcription = get_transcription(file["content"])
    categorized_files.append(
        {"filename": file["filename"], "category": categorize_content(transcription)}
    )


obj = {
    "people": sorted(
        [file["filename"] for file in categorized_files if file["category"] == "people"]
    ),
    "hardware": sorted(
        [
            file["filename"]
            for file in categorized_files
            if file["category"] == "hardware"
        ]
    ),
}


complete_task("kategorie", obj)
