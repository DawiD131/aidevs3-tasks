from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()


def complete_task(task_name, answer):
    print(f"Completing task {task_name} with answer {answer}")
    response = requests.post(
        "https://centrala.ag3nts.org/report",
        json={
            "task": task_name,
            "apikey": os.getenv("TASKS_API_KEY"),
            "answer": answer,
        },
        timeout=(30, 30),  # (connect timeout, read timeout)
    )
    print(response.json())
    return response.json()


def get_tasks_api_key():
    return os.getenv("TASKS_API_KEY")


def get_transcription(path):
    audio_file = open(path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcription.text
