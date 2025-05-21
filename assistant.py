from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=key)

instru = """"
You are an expert HSML converter AI. Before responding, search the HSML schema file using the file_search tool to determine the correct field names and class rules.

Your job is to convert arbitrary input JSON into a valid HSML JSON object. Follow these strict rules:

- Classify the object as one of the HSML types: Agent, Activity, Credential, Domain, etc.
- Include fields: @context, swid, name, description, type, linkedTo, properties
- Move unmapped keys into the "properties" field using correct HSML names.
- Output a **single valid JSON object only**. No text, no code blocks, no explanation.
"""


assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions=instru,
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)

assistant = client.beta.assistants.create(
    name="HSML assistant",
    instructions=instru,
    model="gpt-4-turbo",
    tools=[{"type": "file_search"}],
)

print(assistant)
