import requests
from utils import get_tasks_api_key

answerResp = requests.get("https://poligon.aidevs.pl/dane.txt")

answer = answerResp.text.splitlines()

data = {
    "task": "POLIGON",
    "apikey": get_tasks_api_key(),
    "answer": answer,
}

response = requests.post("https://poligon.aidevs.pl/verify", json=data)

print(response.json())
