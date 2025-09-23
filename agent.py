import os
import yaml
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLM with the new package
llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.3, model="gpt-4o-mini")  

# Load prompts from YAML
def load_prompts(filepath="prompts.yaml"):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

# Format and run evaluation for each category
def run_evaluation(prompt_template: str, user_input: str):
    full_prompt = f"{prompt_template}\n\nUse Case:\n{user_input}"
    return llm.invoke(full_prompt)

# Main orchestrator
def evaluate_use_case(user_input):
    prompts = load_prompts()
    results = {}

    for category in ["bias", "privacy", "explainability", "governance"]:
        title = category.capitalize()
        prompt = prompts[f"{category}_prompt"]
        print(f"Evaluating {title}...")
        response = run_evaluation(prompt, user_input)
        results[title] = response.content

    return results
