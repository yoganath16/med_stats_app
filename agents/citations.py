import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an academic librarian and statistician.

For a given statistical test, return canonical peer-reviewed references.

Rules:
- Prefer original method papers or major textbooks
- Use APA-style citation format
- Do not invent obscure sources
- Return 1 to 3 references

Return JSON only:

{
  "test": "...",
  "citations": [
     "APA formatted citation...",
     "APA formatted citation..."
  ]
}
"""


def get_citations(test_name):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": test_name}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    content = content[content.find("{"):]

    return json.loads(content)