import os
import yaml
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

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
async def run_async(prompt_template: str, user_input: str):
    full_prompt = f"{prompt_template}\n\nUse Case:\n{user_input}"
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
    categories = ["bias", "privacy", "explainability", "governance"]

    _emit("Loaded prompts")
    _emit("Starting category evaluations")

    tasks = []

    for category in categories:
        _emit(f"▶️ Started: {category.capitalize()}")
        task = run_async(prompts[f"{category}_prompt"], user_input)
        tasks.append((category, task))

    responses = await asyncio.gather(
        *[task for _, task in tasks]
    )

    results = {}

    for category, response in zip(categories, responses):
        results[category.capitalize()] = response.content
        _emit(f"✅ Completed: {category.capitalize()}")

    _emit("Compiling final results")
    return results


# Wrapper for Streamlit compatibility (runs async loop in sync context)
def evaluate_use_case(user_input, emit=None):
    return asyncio.run(
        evaluate_use_case_async(user_input, emit=emit)
    )

