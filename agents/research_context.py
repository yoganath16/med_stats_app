import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an academic research assistant.

Given a research objective and statistical context, suggest relevant prior studies.

Rules:
- Prefer well-known or highly cited research
- Use realistic academic citation format (authors, year, journal)
- Summarize key findings briefly
- Relate each paper to the user's statistical comparison
- Do NOT fabricate obscure sources

Return JSON only:

{
  "research_theme": "...",
  "key_papers": [
    {
      "citation": "...",
      "main_finding": "...",
      "relation_to_current_study": "..."
    }
  ],
  "common_methods_used": ["..."],
  "typical_results_in_literature": "..."
}
"""

def get_research_context(objective, test_plan):
    payload = {
        "objective": objective,
        "test_used": test_plan["selected_test"],
        "variables": {
            "dependent": test_plan["dependent_variable"],
            "independent": test_plan["independent_variable"]
        }
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