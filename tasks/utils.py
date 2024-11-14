import requests
import os
from dotenv import load_dotenv

load_dotenv()


def complete_task(task_name, answer):
    print(f"Completing task {task_name} with answer {answer}")
    response = requests.post(
        "https://centrala.ag3nts.org/report",
        json={
            "task": task_name,
            "apikey": os.getenv("TASKS_API_KEY"),
            "answer": answer,
        },
    )
    print(response.json())
    return response.json()


def get_tasks_api_key():
    return os.getenv("TASKS_API_KEY")
