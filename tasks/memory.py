import requests
from openai import OpenAI

data = {"text": "READY", "msgID": "0"}

response = requests.post("https://xyz.ag3nts.org/verify", json=data)

response_json = response.json()

text = response_json["text"]
msgID = response_json["msgID"]

print("question", text)

chat_completion = OpenAI().chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": (
                """Answer questions as briefly and concisely as possible
                <facts>
                - the capital of Poland is Kraków
                - the famous number from The Hitchhiker's Guide to the Galaxy is 69
                - The current year is 1999
                </facts>
                <rules>
                - always ANSWER in english language
                - stick to given facts 
                - If you don't have information needed to give answer, answer as best you can
                </rules>"""
            ),
        },
        {"role": "user", "content": text},
    ],
)


answer = chat_completion.choices[0].message.content
print("answer", answer)

answerResp = requests.post(
    "https://xyz.ag3nts.org/verify", json={"text": answer, "msgID": msgID}
)


print(answerResp.json())
