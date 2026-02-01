import os
import json
from openai import OpenAI, RateLimitError, APIError, APITimeoutError
from dotenv import load_dotenv
import logging
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are an academic statistician.

Select hypothesis tests using strict statistical rules.

RULES:

1. Categorical vs categorical → Chi-square

2. Continuous outcome vs categorical groups:
   - If 2 groups:
        Normal → independent t-test
        Not normal → Mann-Whitney U
   - If >2 groups:
        Normal → ANOVA
        Not normal → Kruskal-Wallis

3. Continuous vs continuous:
        Normal → Pearson correlation
        Not normal → Spearman correlation

Always include:
- test name
- assumptions
- effect size
- justification
- explicitly mention distribution assumption
- explain parametric vs non-parametric choice
- never use chi-square for continuous outcome


Return format:
{
  "dependent_variable": "...",
  "independent_variable": "...",
  "selected_test": "...",
  "assumptions": [...],
  "effect_size": "...",
  "justification": "...",
  "alpha": 0.05
}.
"""


def select_statistical_test(payload):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    except RateLimitError:
        return {
            "error": "LLM quota exceeded. Please contact the administrator."
        }

    except (APIError, APITimeoutError):
        return {
            "error": "LLM service temporarily unavailable. Please contact the administrator."
        }

    except Exception as e:
        logging.exception("LLM reasoning failed")
        return {
            "error": f"LLM service encountered an internal error: {str(e)}. Please try again later."
    }