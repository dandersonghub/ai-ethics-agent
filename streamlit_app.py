import streamlit as st
from agent import evaluate_use_case
from pathlib import Path
from datetime import datetime

# Set Streamlit page config
st.set_page_config(page_title="AI Ethics Assistant", layout="centered")
st.title("🤖 AI Ethics Assistant")
st.markdown("""
Use this tool to evaluate an AI use case for ethical risks in:
- **Bias**  
- **Privacy**  
- **Explainability**  
- **Governance & Oversight**  

_Reports will be saved locally to the `reports/` folder._
""")

# Function to format results as markdown
def format_results_as_markdown(results: dict) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_md = f"# AI Ethics Evaluation Report\n\n**Generated:** {timestamp}\n\n"
    for category, summary in results.items():
        report_md += f"## {category}\n{summary.strip()}\n\n"
    return report_md.strip()

# Input
user_input = st.text_area(
    "Describe your AI use case:",
    placeholder="E.g. An AI model that predicts hospital readmission using patient records, deployed on cloud...",
    height=200
)

if st.button("Evaluate Use Case"):
    if not user_input.strip():
        st.warning("Please enter a description before submitting.")
    else:
        with st.spinner("Evaluating use case..."):
            results = evaluate_use_case(user_input)
            markdown_output = format_results_as_markdown(results)

        st.success("Evaluation complete!")

        # Display results
        st.subheader("📝 Ethics Risk Evaluation")
        st.markdown(markdown_output)

        # Save report to markdown file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = Path("reports") / f"eval_{timestamp}.md"
        filename.write_text(markdown_output, encoding='utf-8')

        st.info(f"Saved to `{filename}`")
