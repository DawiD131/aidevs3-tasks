from requests import get
from utils import complete_task, get_tasks_api_key
from openai import OpenAI

client = OpenAI()
questions = get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/softo.json"
).json()


def getPageContent(url):
    resp = get(url)
    return resp.text


def processQuestion(question, page, visited_urls):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                _thinking

                Before answer analize very carefully all visited pages in <VISITED_URLS> tag. Becouse you can't visit same page twice. 
                <VISITED_URLS>
                {visited_urls}
                </VISITED_URLS>

                _thinking_end
                For given question, try to find answer on given page. 
                If you can't find answer, return appropriate link to the page where possible answer can be found.
                
                Follow instructions in <RULES> tag.
                base page url: https://softo.ag3nts.org
            
                <PAGE>
                {page}s
                </PAGE>

                <RULES>
                - Return only link to the page or briefly answer NOTHING ELSE
                - Never visit same page twice. All visited pages are stored in <VISITED_URLS> tag. It's very important.
                - If you return final answer, return it in format like this: "answer: 'Answer'", if return another link to visit return in format like this: "link: https://example.com"
                </RULES>
            """,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    return resp.choices[0].message.content


answers = {}
visited_urls = ""
for question in questions:

    id = question
    question = questions[question]

    print(f"Question: {question}")
    page = getPageContent("https://softo.ag3nts.org")

    answer = processQuestion(question, page, visited_urls)

    print(f"Answer: {answer}")
    while answer.startswith("link"):
        url = answer.replace("link: ", "")
        visited_urls += f"\n<url>{url}</url>"
        page_content = getPageContent(url)

        resp = processQuestion(question, page_content, visited_urls)

        print(f"Answer: {answer}")
        answer = resp
        answers[id] = answer.replace("answer: ", "").strip("'")


complete_task("softo", answers)
