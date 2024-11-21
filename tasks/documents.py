import os
from openai import OpenAI
from utils import complete_task

client = OpenAI()

facts_dir = os.path.join("tasks", "pliki_z_fabryki", "facts")
doc_dir = os.path.join("tasks", "pliki_z_fabryki")

facts_files = []

for filename in os.listdir(facts_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(facts_dir, filename)
        with open(file_path, "r") as file:
            content = file.read()
            facts_files.append({"filename": filename, "content": content})

facts = "\n####\n".join(fact["content"] for fact in facts_files)


def tag_document(content):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
             <FACTS>
             {facts}
             </FACTS>

            Your task is to perform very detailed and descriptive document tagging based on the provided facts.

             Based on the facts provided in <FACTS>, analyze the document and tag it with appropriate nouns.
             Return a JSON array with tags that represent the document and only that.
             Also tag facts related to the document very thoroughly and descriptively
             RETURN THE MAXIMUM NUMBER OF TAGS POSSIBLE

             It's very important that for people connected to the document, include tags (TAKING INFORMATION FROM <FACTS> and from the document) for:
               * Their full names
               * Their professions and skills
               * Their work departments and units  
               * Sectors they are or were connected with
               * Programming languages they used
               * Their technical skills and competencies

             TAGS MUST BE AS EXTENSIVE AND AS PRECISE AS POSSIBLE, THE DOCUMENT MUST BE TAGGED VERY THOROUGHLY SO GENERATE THE MAXIMUM NUMBER OF TAGS MINIMUM 40

             <RULES>
             - You must tag the document with all facts and document content
             - Return only nouns in nominative case
             - Don't return JSON in a ```json``` block
             - Tags can consist of multiple words to precisely describe the document
             - Tag important facts mentioned in the document or in <FACTS>
             - Tag all places mentioned in the facts
             - Tag the document name
             </RULES>
             """,
            },
            {"role": "system", "content": f"Tag the following document: {content}"},
        ],
    )

    return resp.choices[0].message.content


tagged_files = {}
for filename in os.listdir(doc_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(doc_dir, filename)
        with open(file_path, "r") as file:
            content = file.read()
            tagged_files[filename] = tag_document(f"Filename {filename} " + content)
            print(tagged_files[filename])


complete_task("dokumenty", tagged_files)
