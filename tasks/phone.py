import json
from utils import get_tasks_api_key, complete_task
from requests import get, post
from openai import OpenAI
import os

client = OpenAI()

conversations = get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/phone_sorted.json",
).json()

questions = get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/phone_questions.json"
).json()

facts_dir = os.path.join("tasks", "pliki_z_fabryki", "facts")


facts_files = []

for filename in os.listdir(facts_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(facts_dir, filename)
        with open(file_path, "r") as file:
            content = file.read()
            facts_files.append({"filename": filename, "content": content})

facts = "\n####\n".join(fact["content"] for fact in facts_files)


def inferPeopleNames(conversation):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                _thinking

                <FACTS>
                    {facts}
                </FACTS>

                You are an expert in inferring people names from conversations. 
                Wrap all message in given conversation within name tags like in <example> below.

                Before you start, think step by step what are the names of people in the conversation.
                Analize carefully each message and and get the names right.

                Follow the rules in <Rules> section

                <Rules>
                - When you can't infer names from the conversation, use the facts below to help you.
                - You can't modify original conversation.
                </Rules>

       

                <example>
                user: 
                - Hello, how are you Mark?
                - I am fine, thank you John. How can I help you today?
                - I need to buy a new phone.
                - What kind of phone do you need?

                assistant:
                <john>Hello, how are you Mark?</john>
                <mark>I am fine, thank you John. How can I help you today?</mark>
                <john>I need to buy a new phone.</john>
                <mark>What kind of phone do you need?</mark>
                </example>

                All information for inference is in <FACTS> section. Use it to infer names. Always is possible to infer names from facts.
                """,
            },
            {"role": "user", "content": conversation},
        ],
    )

    return resp.choices[0].message.content


# prepared_conversations = []
# for conversation in conversations:
#     conversationId = conversation
#     conversationText = "\n".join(conversations[conversationId])
#     result = inferPeopleNames(conversationText)
#     print(result)
#     prepared_conversations.append(result)

# with open("tasks/phone/conversations.txt", "w") as f:
#     f.write(
#         "\n".join(
#             [
#                 f"""<conversation{i+1}>
#                 {conv}
#                 </conversation{i+1}>\n"""
#                 for i, conv in enumerate(prepared_conversations)
#             ]
#         )
#     )


def answer(conversations_content, question, tools_results, previous_answers):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                Answer questions connected to conversation in <CONVERSATION> section based on facts in <FACTS>.
                The answer may require using tools available in the <Tools> section. If so, return the response in JSON format containing the necessary information to use the tool as shown in the <example> section.
                If the answer does not require using tools, return the final answer in JSON format.

                Results of previously executed tools or answers can be found in the <PREVIOUS_ANSWERS> section analize them carefully too.

                Follow the rules in <Rules> section.
                _thinking

                <CONVERSATION>
                {conversations_content}
                </CONVERSATION>


                <FACTS>
                {facts}
                </FACTS>

            
                <PREVIOUS_ANSWERS>
                {previous_answers}

                {"\n".join(tools_results)}
                </PREVIOUS_ANSWERS>

    
                <Rules>
                - Don't return json in ```json``` block.
                - Answer must be in JSON format.
                - Base on <PREVIOUS_ANSWERS> section when answering questions.
                </Rules>

                <examples>
                  user: co znajduje się w endpoincie http://example.com/api
                  ai: {{
                    "tool": "api_post",
                    "final_answer": false,
                    "params": {{
                        "url": "http://example.com/api",
                        "body": "this is body of api post call"
                    }}
                  }}


                  user: Kim jest Andrzej?
                  ai: {{
                    "answer": "Andrzej jest programistą",
                    "final_answer": true
                  }}
                <example>

    

                <Tools>
                 <api_post>
                  <params>
                    <body>
                        this is body of api post call
                    </body>
                    <url>
                        this is url of api post call
                    </url>
                  </params>
                 </api_post>
                <Tools>


           
            """,
            },
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content


def api_post(url, body):
    resp = post(url, json=body)
    return resp.json()


print(questions)


with open("tasks/phone/conversations.txt", "r") as f:
    conversations_content = f.read()

    answered_questions = {}
    tools_results = []
    previous_answers = []

    for question in questions:
        question_id = question
        question_text = questions[question_id]

        final_answer = False

        while not final_answer:
            resp = answer(
                conversations_content,
                question_text,
                tools_results,
                "\n".join(previous_answers),
            )
            print(resp)

            answer_json = json.loads(resp)

            if answer_json["final_answer"]:
                answered_questions[question_id] = answer_json["answer"]
                previous_answers.append(
                    f"""
                    <question_{question_id}>
                        <question>{question_text}</question>
                        <answer>{answer_json["answer"]}</answer>
                    </question_{question_id}>
                    """
                )
                final_answer = True
            else:
                body = answer_json["params"]["body"]
                url = answer_json["params"]["url"]
                result = api_post(url, body)
                tools_results.append(
                    f"""
                <api_post>
                <params>
                    <body>
                        {body}
                    </body>
                    <url>
                        {url}
                    </url>
                  </params>

                  <result>
                    {result}
                  </result>
                </api_post>
                """
                )

complete_task(
    "phone",
    answered_questions,
)
