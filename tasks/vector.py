from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import numpy as np
from qdrant_client.models import PointStruct
import os
from utils import complete_task


q_client = QdrantClient(
    url="https://07e3617a-739c-42de-939d-b9ea4378a3e2.us-east4-0.gcp.cloud.qdrant.io:6333",
    api_key="7Q6EVkNCdSFhblO6Db-rjnow2Q05ECliGkP_Y4mbMXVNGFMqgNgkBw",
)

if not q_client.collection_exists("aidevs3"):
    q_client.create_collection(
        collection_name="aidevs3",
        vectors_config=VectorParams(size=100, distance=Distance.COSINE),
    )

client = OpenAI()


def create_embedding(text):
    response = client.embeddings.create(
        input=text, model="text-embedding-3-large", dimensions=100
    )

    return response.data[0].embedding


doc_dir = os.path.join("tasks", "pliki_z_fabryki", "do-not-share")


embedded_docs = []

for filename in os.listdir(doc_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(doc_dir, filename)
        with open(file_path, "r") as file:
            content = file.read()
            vector = create_embedding(content)
            meta = {"date": filename.replace(".txt", "")}
            embedded_docs.append({"filename": filename, "vector": vector, "meta": meta})


q_client.upsert(
    collection_name="aidevs3",
    points=[
        PointStruct(
            id=idx,
            vector=doc["vector"],
            payload={"filename": doc["filename"], "meta": doc["meta"]},
        )
        for idx, doc in enumerate(embedded_docs)
    ],
)

query_vector = create_embedding(
    "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
)

hits = q_client.search(
    collection_name="aidevs3",
    query_vector=query_vector,
    limit=1,
)

answer = hits[0].payload["filename"].replace("_", "-").replace(".txt", "")


complete_task(
    "wektory",
    answer,
)
