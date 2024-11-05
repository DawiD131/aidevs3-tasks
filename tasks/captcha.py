import time

from playwright.sync_api import sync_playwright
from openai import OpenAI


def open_website():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://xyz.ag3nts.org")

        page.fill('input[name="username"]', "tester")

        page.fill('input[name="password"]', "574e112a")

        question_text = page.locator("#human-question").text_content()

        chat_completion = OpenAI().chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Answer as short as possible"},
                {"role": "user", "content": question_text},
            ],
        )

        page.fill('input[name="answer"]', chat_completion.choices[0].message.content)

        page.click("button#submit")

        time.sleep(5)

        browser.close()


open_website()
