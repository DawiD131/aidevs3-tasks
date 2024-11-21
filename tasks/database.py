#  https://centrala.ag3nts.org/apidb
# {"task": "database", "apikey": "Twój klucz API", "query": "select * from users limit 1"}

from requests import post
from utils import complete_task, get_tasks_api_key
from openai import OpenAI

client = OpenAI()
api_key = get_tasks_api_key()


def perform_db_query(query):
    tables_resp = post(
        "https://centrala.ag3nts.org/apidb",
        json={
            "task": "database",
            "apikey": api_key,
            "query": query,
        },
    )
    return tables_resp.json()["reply"]


def get_table_structure(name):
    resp = post(
        "https://centrala.ag3nts.org/apidb",
        json={
            "task": "database",
            "apikey": api_key,
            "query": f"show create table {name}",
        },
    )
    return resp.json()["reply"][0]


table_names = perform_db_query("show tables")
table_names = [table["Tables_in_banan"] for table in table_names]


def get_tables_information():
    informations = []
    for table_name in table_names:
        resp = get_table_structure(table_name)
        informations.append(
            f"""
            <TABLE>
                <NAME>{table_name}</NAME>
                <STRUCTURE>{resp["Create Table"]}</STRUCTURE>
            </TABLE>
        """
        )
    return "\n".join(informations)


answer = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": f"""
            You are a database expert.
            You are given a list of tables and their structures.
            For given query you have to return correct sql query.

            - Return only sql query, nothing else.
            - Sql code must not be in ```sql``` code block.
        
            <DB>
                {get_tables_information()}
            </DB>
            """,
        },
        {
            "role": "user",
            "content": "które aktywne datacenter (DC_ID) są zarządzane przez pracowników, którzy są na urlopie (is_active=0)",
        },
    ],
)

query_results = perform_db_query(answer.choices[0].message.content)

answer = [result["dc_id"] for result in query_results]
complete_task("database", answer)
