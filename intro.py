import requests

answerResp = requests.get("https://poligon.aidevs.pl/dane.txt")

answer = answerResp.text.splitlines()

data = {
    "task": "POLIGON",
    "apikey": "a6f443b2-e7fc-4f27-ac4e-c0ec9b3c370c",
    "answer": answer,
}

response = requests.post("https://poligon.aidevs.pl/verify", json=data)
print(response.json())
