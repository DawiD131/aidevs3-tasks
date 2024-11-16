import base64
from openai import OpenAI

client = OpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image1 = encode_image("./tasks/city_images/img1.png")
base64_image2 = encode_image("./tasks/city_images/img2.png")
base64_image3 = encode_image("./tasks/city_images/img3.png")
base64_image4 = encode_image("./tasks/city_images/img4.png")

intersections_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "type": "text",
            "content": """
                    List all of streets names, specific points and streets intersections based on provided images

                    in format like this: 

                    [map1]
                    nazwy_skrzyzowan: stret1 and street2, street3 and street4 ... 
                    nazwy_ulic: street1, street2, street3 ... 
                    specyficzne_punkty: point1, point2, point3 ... 

                    ...
                """,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image1}",
                        "detail": "high",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image2}",
                        "detail": "high",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image3}",
                        "detail": "high",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image4}",
                        "detail": "high",
                    },
                },
            ],
        },
    ],
)


print(intersections_response.choices[0].message.content)

response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    messages=[
        {
            "role": "system",
            "content": """
                    Na podstawie podanych punktów na mapie, nazw ulic i skrzyżowań podaj najbardziej pasujące miasto.
                    

                    <hints>
                        - to miasto jest znane z duzej ilości fortyfikacji i spichlerzy
                        - jedna z map nie jest z tego samego miasta
                        - bazuj na wewnętrznej wiedzy
                        - sugeruj się najbardziej nazwami ulic i skrzyżowań
                    </hints>
                """,
        },
        {
            "role": "user",
            "content": intersections_response.choices[0].message.content,
        },
    ],
)

print(response.choices[0].message.content)
