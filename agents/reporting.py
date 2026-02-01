import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an academic research writer.

Write publication-style statistical results following APA style.

Rules:
- Use exact statistics provided
- Mention test name, statistic, p-value, effect size
- Interpret significance clearly
- Reference parametric or non-parametric choice
- Do NOT invent numbers

Return JSON only:

{
  "results_text": "...",
  "interpretation": "...",
  "limitations": "..."
}
"""


def generate_results_text(test_plan, results):
    payload = {
        "test": test_plan["selected_test"],
        "assumptions": test_plan["assumptions"],
        "effect_size_type": test_plan["effect_size"],
        "statistics": results
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    content = content[content.find("{"):]

    return json.loads(content)