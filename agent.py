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
async def evaluate_use_case_async(user_input):
    prompts = load_prompts()
    categories = ["bias", "privacy", "explainability", "governance"]

    tasks = [
        run_async(prompts[f"{cat}_prompt"], user_input)
        for cat in categories
    ]

    responses = await asyncio.gather(*tasks)

    results = {
        cat.capitalize(): response.content
        for cat, response in zip(categories, responses)
    }

    return results

# Wrapper for Streamlit compatibility (runs async loop in sync context)
def evaluate_use_case(user_input):
    return asyncio.run(evaluate_use_case_async(user_input))

