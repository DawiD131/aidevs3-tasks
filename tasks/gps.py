import json
from openai import OpenAI
from utils import get_tasks_api_key, complete_task
from requests import get, post


client = OpenAI()

resp = get(f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/gps.txt")


questions = get(
    f"https://centrala.ag3nts.org/data/{get_tasks_api_key()}/gps_question.json"
).json()


def perform_db_query(query):
    tables_resp = post(
        "https://centrala.ag3nts.org/apidb",
        json={
            "task": "database",
            "apikey": get_tasks_api_key(),
            "query": query,
        },
    )
    return tables_resp.json()["reply"]


def get_people_by_location():
    resp = post(
        "https://centrala.ag3nts.org/places",
        json={
            "apikey": get_tasks_api_key(),
            "query": {
                "lat": "123.396256",
                "lon": "123.508731",
            },
        },
    )
    return resp.json()


def gps(userID, username):
    print(userID)
    resp = post(
        "https://centrala.ag3nts.org/gps",
        json={"apikey": get_tasks_api_key(), "userID": userID},
    )
    return resp.text


def plan(question, previous_execution_result):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                _thinking
                Don't execute tools with same arguments twice!

                <tools_execution_result>
                    {"\n".join(previous_execution_result)}
                </tools_execution_result>

                Your task is to schdule next step to find people location. 
                You have to use only one tool per step.
                All already executed tools are in <tools_execution_result> tag.
                When generate next step analize carefully what tools are already executed and check it's result

                Return only JSON with next tool to execute to find people locations.

                <tools>

                <tool>
                    <tool_name>gps</tool_name>
                    <description>Get single user location by user id from DB</description>
                    <arguments>
                       <userID>
                        <description>An user id from DB</description>
                        <type>string</type>
                        <required>true</required>
                       </userID>
                       <username>
                        <description>An username from DB</description>
                        <type>string</type>
                        <required>true</required>
                       </username>
                    </arguments>
                </tool>

                <tool>
                    <tool_name>perform_db_query</tool_name>
                    <description>Perform a standard SQL query</description>
                    <db_schema>
                        <table>
                            <name>users</name>
                            <columns>
                                <column>id</column>
                                <column>username</column>
                            </columns>
                        </table>
                    </db_schema>
                    <arguments>
                       <query>
                        <description>Standard SQL query</description>
                        <type>string</type>
                        <required>true</required>
                       </userID>
                    </arguments>
                </tool>

                <tool>
                    <tool_name>get_people_by_location</tool_name>
                    <arguments>
                       <location>
                        <description>A location name to find people</description>
                        <type>string</type>
                        <required>true</required>
                       </location>
                    </arguments>

                    <returns>
                        <people>
                            <description>A list of people</description>
                            <type>array</type>
                        </people>
                    </returns>
                </tool>

                <tool>
                    <tool_name>final_answer</tool_name>
                    <arguments>
                       <locations>
                        <description>An gps tool results for all checked people from get_people_by_location tool</description>
                        <type>Array</type>
                        <required>true</required>
                       </locations>
                    </arguments>

                    <returns>
                        <locations>
                            <description>A list people locations</description>
                            <type>array</type>

                            <example>
                             {{"locations": [{{"username": "John", "location": {{"lat": 123, "lon": 456}}}}]}}
                            </example>
                        </locations>
                    </returns>
                </tool>
                </tools>

                Don't return json in ```json``` block.
                arguments must be the same as in tool <arguments> tag.
                return all information about tool like it's name and arguments
                
            """,
            },
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content


def final_answer(locations):
    result = {}

    for location in locations:
        result[location["username"]] = {
            "lat": location["location"]["lat"],
            "lon": location["location"]["lon"],
        }

    complete_task("gps", result)


tools = {
    "gps": lambda params: gps(**params),
    "perform_db_query": lambda params: perform_db_query(**params),
    "get_people_by_location": lambda params: get_people_by_location(**params),
    "final_answer": lambda params: final_answer(**params),
}

previous_execution_result = []

# while True:
#     plan_result = json.loads(plan(questions["question"], previous_execution_result))

#     tool_name = plan_result["tool_name"]
#     tool_params = plan_result["arguments"]

#     tool_result = tools[tool_name](
#         {
#             key: value if isinstance(value, list) else str(value)
#             for key, value in tool_params.items()
#         }
#     )

#     if tool_name == "final_answer":
#         break

#     previous_execution_result.append(
#         f"""
#         <{tool_name}>
#             <arguments>{json.dumps(tool_params)}</arguments>
#             <result>{tool_result}</result>
#         </{tool_name}> \n
#         """
#     )
