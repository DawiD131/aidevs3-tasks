from requests import post
from utils import complete_task, get_tasks_api_key
from neo4j import GraphDatabase


api_key = get_tasks_api_key()
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "12345678")


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


connections = perform_db_query("select * from connections")


def clear_db(driver):
    summary = driver.execute_query(
        """
    MATCH (n)
    DETACH DELETE n
    """,
        database_="neo4j",
    ).summary

    print(
        "Deleted {nodes_deleted} nodes and {relationships_deleted} relationships.".format(
            nodes_deleted=summary.counters.nodes_deleted,
            relationships_deleted=summary.counters.relationships_deleted,
        )
    )


def feed_users(driver):
    users = perform_db_query("select * from users")
    summary = driver.execute_query(
        """
    UNWIND $users AS user
    CREATE (:User {id: user.id, username: user.username})
    """,
        users=users,
        database_="neo4j",
    ).summary

    print(
        "Created {nodes_created} nodes in {time} ms.".format(
            nodes_created=summary.counters.nodes_created,
            time=summary.result_available_after,
        )
    )


def feed_connections(driver):
    connections = perform_db_query("select * from connections")
    summary = driver.execute_query(
        """
    UNWIND $connections AS connection
    MATCH (user1:User {id: connection.user1_id})
    MATCH (user2:User {id: connection.user2_id})
    CREATE (user1)-[:KNOWS]->(user2)
    """,
        connections=connections,
        database_="neo4j",
    ).summary

    print(
        "Created {relationships_created} relationships in {time} ms.".format(
            relationships_created=summary.counters.relationships_created,
            time=summary.result_available_after,
        )
    )


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    clear_db(driver)
    feed_users(driver)
    feed_connections(driver)

    def find_shortest_path(driver, from_user, to_user):
        result = driver.execute_query(
            """
            MATCH (start:User {username: $from_user}),
                  (end:User {username: $to_user}),
                  path = shortestPath((start)-[:KNOWS*]-(end))
            RETURN [node IN nodes(path) | node.username] AS users,
                   length(path) AS path_length
            """,
            from_user=from_user,
            to_user=to_user,
            database_="neo4j",
        )
        return result.records

    path = find_shortest_path(driver, "Rafał", "Barbara")
    complete_task("connections", ", ".join(path[0]["users"]))
