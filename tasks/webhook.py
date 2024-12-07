from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()
client = OpenAI()


def analize_instructions(instruction: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                _thinking
            You are a drone pilot navigator. 
            Your task is to answer what object are below the drone at final point. Based on provided map. Map is provided <MAP> tag. It's a 4x4 surface. 
            Each field on map has it's own point and description ex (1x1)[start point]

            Answer with object name in polish language.
            Drone always starts at the start point.
    
            You could get more than one instruction so analize all of them carefultty step by step.
            
            <MAP>
             (1x1)[Start point] (1x2)[grass] (1x3)[tree] (1x4)[home]
             (2x1)[grass] (2x2)[mill] (2x3)[grass] (2x4)[grass]
             (3x1)[grass] (3x2)[grass] (3x3)[rocks] (3x4)[trees]
             (4x1)[mountains] (4x2)[mountains] (4x3)[car] (4x4)[cave]
            </MAP>

            Analize all instruction step by step.

            """,
            },
            {"role": "user", "content": instruction},
        ],
    )
    return response.choices[0].message.content


def get_final_point(instruction: str):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "What is final point of drone after all instructions? Return only object name in polish language.",
            },
            {"role": "user", "content": instruction},
        ],
    )
    return resp.choices[0].message.content


def get_answer(instruction: str):
    return get_final_point(analize_instructions(instruction))


@app.post("/api/answer")
async def answer(request: Request):

    data = await request.json()

    answer = get_answer(data["instruction"])

    print(answer)
    return {"description": answer}
