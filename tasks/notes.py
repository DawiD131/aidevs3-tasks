from utils import complete_task, get_tasks_api_key
from requests import get
import pypdf
import base64
from openai import OpenAI

client = OpenAI()

reader = pypdf.PdfReader("./tasks/notatnik-rafala.pdf")


texts = []
images = []
for page in reader.pages:
    texts.append(page.extract_text())

    # for image in page.images:
    #     image_b64 = base64.b64encode(image.data).decode("utf-8")
    #     images.append(image_b64)

texts.append(
    """
Wszystko zostało zaplanowane. Jestem gotowy, a Andrzej przyjdzie tutaj niebawem. Barbara mówi, że dobrze robię i mam się nie bać. Kolejne pokolenia mi za to wszystkiego podziękują. Władza robotów w 2238 nie nastąpi, a sztuczna inteligencja będzie tylko narzędziem w rękach ludzi, a nie na odwrót. To jest ważne. Wszystko mi się miesza, ale Barbara obiecała, że po wykonaniu zadania wykonamy skok do czasów, gdzie moje schorzenie jest w pełni uleczalne. Wróci moja dawna osobowość. Wróci normalność i uroki tąd w mojej głowie. To wszystko jest na wyciągnięcie ręki. Muszę tylko poczekać na Andrzeja, a później wziąć jego samochód, aby się dostać do Lubawy koło Grudziądza. Nie jest to daleko. Mam tylko nadzieję, że Andrzejek będzie miał dostatecznie dużo paliwa. Tankowanie nie wchodzi w grę, bo nie mam kasy.
"""
)


def extractText(img):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You have perfect vision and can see the text in the image. Extract the text from the image. If there is no text, return 'null'.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                    }
                ],
            },
        ],
    )
    return resp.choices[0].message.content


for image in images:
    result = extractText(image)
    if result != "null":
        texts.append(result)


def get_questions():
    resp = get(f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/notes.json")
    return resp.json()


def format_notes(notes):
    formatted_notes = []
    for note in notes:
        formatted_notes.append(f"<NOTE>{note}</NOTE>")
    return "\n".join(formatted_notes)


notes = format_notes(texts)


def answer_question(question):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                Based on notes available in <NOTES> tag and your internal knowledge answer to user question.


               {notes}


            Follow these __thinking__ steps:
            1. Analyze carefully all facts and events or dates and times given in <NOTES> tag.
            2. Analize user question and think step by step how to answer it based on <NOTES> tag and your knowledge.
            3. If you are not sure about answer, refer to your internal knowledge for support.
            4. If you are not sure about answer repeat steps from 1 to 3.

            5. Answer the question precisely and concisely with concrete answer linke dates or city names.
      
            Answer only with precise answer if needed base on your internal knowledge.
             """,
            },
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content


print(notes)
# questions = get_questions()
# answers = {}
# for questionId in questions:
#     questionId = questionId
#     question = questions[questionId]
#     answer = answer_question(question)

#     answers[questionId] = answer


# complete_task("notes", answers)
