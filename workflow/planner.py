import json
from typing import Callable, Optional

from langchain_openai import ChatOpenAI
from workflow.types import Plan

REQUIRED_CATEGORIES = ["bias", "privacy", "explainability", "governance"]

PLANNER_PROMPT = """
You are an AI planning agent for an AI Ethics evaluation workflow.

Return ONLY valid JSON (no markdown, no code fences, no commentary).

Your job:
1) Decide which categories to run from:
   - bias
   - privacy
   - explainability
   - governance

2) Decide depth per chosen category:
   - quick (short, high-level)
   - standard (balanced)
   - deep (detailed, more thorough)

3) If the use case is missing key details, include 1–4 follow_up_questions.

Heuristics (examples):
- healthcare/PHI/medical images -> privacy=deep, governance=deep, bias=deep, explainability=standard/deep
- hiring/credit/education decisions -> bias=deep, explainability=deep/standard, governance=standard, privacy=standard
- minors/children -> privacy=deep, governance=deep
- biometrics/surveillance/location tracking -> privacy=deep, governance=deep, bias=standard/deep

Rules:
- categories must be a non-empty list of valid category strings.
- depth must include an entry for every category in categories.
- follow_up_questions may be empty.
- Always include all four categories: bias, privacy, explainability, governance.
- You may vary depth per category, but categories must contain all four.

JSON schema example:
{
  "categories": ["bias","privacy","explainability","governance"],
  "depth": {"bias":"deep","privacy":"deep","explainability":"standard","governance":"standard"},
  "follow_up_questions": ["question 1", "question 2"]
}
""".strip()

def _parse_plan(text: str) -> Plan:
    data = json.loads(text)
    return Plan.model_validate(data)

def _enforce_required_categories(plan: Plan) -> Plan:
    # Force categories to always include the required set in a consistent order
    plan.categories = REQUIRED_CATEGORIES

    # Ensure every required category has a depth (default to standard)
    for c in REQUIRED_CATEGORIES:
        plan.depth.setdefault(c, "standard")

    return plan

async def make_plan(
    llm: ChatOpenAI,
    user_input: str,
    emit: Optional[Callable[[str], None]] = None,
) -> Plan:
    def _emit(msg: str) -> None:
        if emit:
            emit(msg)

    _emit("🧠 Planner: analyzing use case")
    msg = f"{PLANNER_PROMPT}\n\nUSE CASE:\n{user_input}"

    # Attempt 1
    resp1 = await llm.ainvoke(msg)
    text1 = resp1.content.strip()

    try:
        plan = _enforce_required_categories(_parse_plan(text1))
        _emit("🧠 Planner: plan created (valid JSON)")
        return plan

    except Exception as e1:
        _emit("🧠 Planner: invalid JSON, retrying once")

        # Attempt 2: ask to fix JSON, include original output + error
        fix_msg = (
            "Your previous output was not valid JSON or didn't match the schema.\n"
            "Return ONLY corrected valid JSON.\n\n"
            f"ERROR: {str(e1)}\n\n"
            f"PREVIOUS OUTPUT:\n{text1}\n\n"
            f"USE CASE:\n{user_input}"
        )
        resp2 = await llm.ainvoke(fix_msg)
        text2 = resp2.content.strip()

        plan = _enforce_required_categories(_parse_plan(text2))
        _emit("🧠 Planner: plan created (valid JSON after retry)")
        return plan


