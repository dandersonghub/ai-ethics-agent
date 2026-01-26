import streamlit as st
from agent import evaluate_use_case
from pathlib import Path
from datetime import datetime
import time 
import html


# Streamlit page config
st.set_page_config(page_title="AI Ethics Agent", layout="centered")
MODEL_NAME = "gpt-4o-mini"
if "step_log" not in st.session_state:
    st.session_state.step_log = []
st.title("🛡️ AI Ethics Agent")
st.markdown(
    """
This tool evaluates an AI use case across **four key ethical risk areas**:
- **Bias**
- **Privacy**
- **Explainability**
- **Governance & Oversight**

💡 Understanding these areas is critical before deploying any AI solution, especially for systems that impact real people. This tool helps uncover ethical risks you may not have considered.

When you click **Evaluate Use Case**, the app generates an **AI Use Case Evaluation Report** and provides download options.
"""
)

# Input box
user_input = st.text_area(
    "Describe your AI use case:",
    placeholder=(
        "E.g.\n"
        "1. An AI model that predicts hospital readmission using patient records, deployed on cloud.\n"
        "2. A chatbot that provides mental health support to teenagers via a mobile app.\n"
        "3. A facial recognition system used for access control in a corporate office.\n"
        "\n"
        "Full Example:\n"
        "A machine learning system that analyzes loan applications to predict credit risk. The model uses demographic, financial, and behavioral data, and is integrated into an online banking platform to automate loan approvals."
    ),
    height=250,
    key="use_case_input"
)

if st.button("Evaluate Use Case"):
    if not user_input.strip():
        st.warning("Please enter a description before submitting.")
    else:
        progress = st.progress(0, text="Evaluating ethical risks...")
        
        # Clear previous run's steps
        st.session_state.step_log = []

        # Live processing feed
        st.subheader("🔎 Agent Processing")
        step_box = st.empty()

        def emit(step: str):
            st.session_state.step_log.append(step)
            step_box.markdown("\n".join([f"- {s}" for s in st.session_state.step_log]))

        run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()
        
        results, plan = evaluate_use_case(user_input, emit=emit)

        
        duration_s = round(time.time() - start_time, 2)
        
        progress.progress(100, text="✅ Evaluation complete!")
        
        # --- Plan Summary (quick glance for users) ---
        st.subheader("🧭 Evaluation Plan")

        depth_summary = ", ".join([f"{c.capitalize()} ({plan.depth.get(c, 'standard')})" for c in plan.categories])
        st.markdown(f"- **Categories:** {', '.join([c.capitalize() for c in plan.categories])}")
        st.markdown(f"- **Depth:** {depth_summary}")
        st.markdown(f"- **Follow-ups suggested:** {len(plan.follow_up_questions)}")




        # Build Markdown-style string for report
        markdown_content = f"# AI Use Case Evaluation Report\n\n**Use Case:**\n{user_input.strip()}\n\n"
        # Optional: show follow-up questions if planner needs more detail
        if plan.follow_up_questions:
            markdown_content += "## Follow-up Questions (to improve accuracy)\n"
            for q in plan.follow_up_questions:
                markdown_content += f"- {q}\n"
            markdown_content += "\n"

        for key, value in results.items():
            markdown_content += f"## {key}\n{value.strip()}\n\n"

        markdown_content += (
            "---\n\n"
            "## Report Metadata\n"
            f"- **Timestamp:** {run_timestamp}\n"
            f"- **Model:** {MODEL_NAME}\n"
            f"- **Runtime (seconds):** {duration_s}\n"
        )
        
        # Save Markdown file to reports/
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        md_path = reports_dir / f"eval_{timestamp}.md"
        md_path.write_text(markdown_content, encoding="utf-8")
      
        # --- Downloads (placed directly before report) ---
        st.markdown("### ⬇️ Download Report")

        # Build HTML version for download
        html_report = (
            "<html><head><meta charset='utf-8'></head><body>"
            + "<pre style='white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;'>"
            + html.escape(markdown_content)
            + "</pre></body></html>"
        )

        # Tight layout: small gap + aligned buttons
        col1, col2, col3 = st.columns([2, 2, 4], gap="small")

        with col1:
            st.download_button(
                label="⬇️ Download .md",
                data=markdown_content.encode("utf-8"),
                file_name=f"eval_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:
            st.download_button(
                label="⬇️ Download .html",
                data=html_report.encode("utf-8"),
                file_name=f"eval_{timestamp}.html",
                mime="text/html",
                use_container_width=True,
            )


        # Display report (bordered)
        st.subheader("✅ Evaluation Results")
        with st.container(border=True):
            st.markdown(markdown_content)

               
        # Display report
        st.subheader("✅ Evaluation Results")

        with st.container(border=True):
            st.markdown(markdown_content)



