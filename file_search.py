import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

client = OpenAI(api_key=key)

# create a vector store
vector_store = client.vector_stores.create(name="HSML")
print(vector_store)


# upload file
file_path = r"/Users/diego/Desktop/HSML Schema Doc v1 2-3-25.txt"

uploaded_file = client.files.create(file=open(file_path, "rb"), purpose="assistants")


vector_store_file_batch = client.vector_stores.file_batches.create(
    vector_store_id=vector_store.id,
    file_ids=[uploaded_file.id],
)
print(vector_store_file_batch)


# create assitant with the vector store
assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
print("assistant updated with vector store")

# create a thread
thread = client.beta.threads.create()
print(f"Your thread is - {thread.id}\n\n")


text = """"
{
  "id": "event-123",
  "title": "Annual Developer Conference",
  "organizer": {
    "name": "TechCorp",
    "email": "contact@techcorp.com"
  },
  "startTime": "2025-09-15T09:00:00Z",
  "endTime": "2025-09-15T17:00:00Z",
  "location": "San Francisco, CA",
  "attendees": [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Lee", "email": "bob@example.com"}
  ],
  "description": "A full-day conference exploring trends in AI and software engineering.",
  "tags": ["conference", "AI", "development"]
}
    """

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=text,
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant_id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
message_content = messages[0].content[0].text.value
print("Response : \n")
print(f"{message_content}\n")


"""""
while True:
    text = input("Input JSON to covert to HSML/n")

    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role = "user",
        context = text,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id= assistant_id
    )

    messages = list(client.beta.threads.messages.list(thread_id = thread.id, run_id= run.id))
    message_content = message[0].content[0].text
    print("Response : \n")
    print(f"{message_content.value}\n")
"""
