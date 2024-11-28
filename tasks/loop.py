import json
from requests import get, post
from utils import get_tasks_api_key, complete_task
from openai import OpenAI

client = OpenAI()
note = get("https://centrala.ag3nts.org/dane/barbara.txt").text


def extract_information_from_note(results):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                IT's IMPORTANT TO RETURN ONLY JSON AND NOTHING ELSE.

                <RESULTS>
                  {results}
                <RESULTS>

                You are detective. 
                Your task is to find where Barbara is NOW.
                You will be called appropriate tools from <TOOLS> section to get information about places and people.
                Each tool's execution result will be added to <RESULTS> section.
                By using tools you can get connections between where people were by given place or where people are by given person first name.
            

                <RESULTS> section is for you to remember what you already did. 
                Each result contains tool name, arguments which you already used and result of tool execution.

                Follow <THINKING> section to decide what to do.
                
                DON'T USE TOOLS WITH SAME ARGUMENTS TWICE.
                
                <TOOLS>
                - [id: places](first_name: first name of person in upper case, without polish letters): It returns list of places. get information about places by person name. It returns places where person was. 
                 - [id: people](place: place name in upper case, without polish letters): It returns list of people first names. get information about people by place name. It returns people who were in given place.
                 - [id: check](place: place name in upper case, without polish letters) check if Barbara is in given place. It returns appropriate message when Barbara is in given place.
                </TOOLS>
                 
                <NOTE>
                  {note}
                <NOTE>

                <THINKING>
                 0. Analyse carefully each result in 
                 1. If there is no any <RESULTS> yet analyse note and decide what to do at first.
                 2. Check correct tool to use by analysing <RESULTS> section.
                 3. <thinking> Check all <RESULTS> VERY CAREFULLY and make sure you didn't use some tool with same arguments twice.
                 4. Analize all <RESULTS> and conclude possible connections between places and people.
                 5. Before using tool check if you already used it with same arguments.
                 6. Return tool name and arguments in JSON format like <RULES> section says.
                </THINKING>

                <RULES>
                - Dont' return JSON in a ```json``` block
                - Don't use tool with same arguments twice so check <RESULTS> section before using it again. It's very important
                - Remember to check city names by check tool
                - Some tools may return an error etc.. so check result before using it again and try to use different tools or different arguments
                - Return only tool name and arguments in JSON format and nothing else like this:
                  {{
                    "tool": "toole_name",
                    "args": {{"first_name": "FIRST_NAME"}}
                 }}
                </RULES>

                IT's IMPORTANT TO RETURN ONLY JSON AND NOTHING ELSE.
                                            
        """,
            },
            {"role": "system", "content": f"Where is Barbara?"},
        ],
    )
    return resp.choices[0].message.content


def places(first_name):
    resp = post(
        "https://centrala.ag3nts.org/people",
        json={"apikey": get_tasks_api_key(), "query": first_name},
    )

    return f"<TOOL_RESULT>\n  <tool_name>places</tool_name>\n  <message>{resp.json()['message']}</message>\n  <arguments>first_name: {first_name}</arguments>\n</TOOL_RESULT>"


def people(place):
    resp = post(
        "https://centrala.ag3nts.org/places",
        json={"apikey": get_tasks_api_key(), "query": place},
    )

    return f"<TOOL_RESULT>\n  <tool_name>people</tool_name>\n  <message>{resp.json()['message']}</message>\n  <arguments>place: {place}</arguments>\n</TOOL_RESULT>"


def check(place):
    resp = complete_task("loop", place)

    return f"<TOOL_RESULT>\n  <tool_name>check</tool_name>\n  <message>{resp['message']}</message>\n  <arguments>place: {place}</arguments>\n</TOOL_RESULT>"


tools = {
    "places": places,
    "people": people,
    "check": check,
}


results = ""


def run(results):
    resp = extract_information_from_note(results)
    print(resp)

    resp = json.loads(resp)

    tool_name = resp["tool"]
    tool_args = resp["args"]
    tool_fn = tools[tool_name]

    results += tool_fn(**tool_args) + "\n"

    run(results)


run(results)
