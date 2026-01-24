import os
import yaml
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from workflow.planner import make_plan


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.3, model="gpt-4o-mini")

# Load prompts from YAML
def load_prompts(filepath="prompts.yaml"):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

# Async evaluation function
async def run_async(prompt_template: str, user_input: str, depth: str):
    depth_instruction = f"\n\nEvaluation depth: {depth.upper()}.\n"
    depth_instruction += (
        "If QUICK: be concise.\n"
        "If STANDARD: balanced detail.\n"
        "If DEEP: be thorough, include edge cases and mitigations.\n"
    )
    full_prompt = f"{prompt_template}{depth_instruction}\n\nUse Case:\n{user_input}"
    return await llm.ainvoke(full_prompt)


# Main orchestrator (async)
async def evaluate_use_case_async(
    user_input: str,
    emit=None,
):
    """
    Evaluate a use case across ethics categories concurrently.
    If `emit` is provided, it will be called with step messages for UI progress.
    """

    def _emit(message: str):
        if emit:
            emit(message)

    prompts = load_prompts()  
    _emit("Loaded prompts")

    # --- Planner step ---
    plan = await make_plan(llm, user_input, emit=emit)
    categories = plan.categories

    _emit(f"🧠 Planner: categories = {', '.join([c.capitalize() for c in categories])}")
    for c in categories:
        _emit(f"🧠 Planner: depth[{c}] = {plan.depth.get(c, 'standard')}")
    if plan.follow_up_questions:
        _emit(f"🧠 Planner: {len(plan.follow_up_questions)} follow-up question(s) generated")

    _emit("Starting category evaluations")

    # --- Run planned categories concurrently ---
    tasks = []
    for category in categories:
        depth = plan.depth.get(category, "standard")
        _emit(f"▶️ Started: {category.capitalize()} ({depth})")
        task = run_async(prompts[f"{category}_prompt"], user_input, depth)
        tasks.append((category, task))

    responses = await asyncio.gather(*[task for _, task in tasks])

    results = {}
    for category, response in zip(categories, responses):
        results[category.capitalize()] = response.content
        _emit(f"✅ Completed: {category.capitalize()}")

    _emit("Compiling final results")
    return results, plan

# Wrapper for Streamlit compatibility (runs async loop in sync context)
def evaluate_use_case(user_input, emit=None):
    return asyncio.run(
        evaluate_use_case_async(user_input, emit=emit)
    )

