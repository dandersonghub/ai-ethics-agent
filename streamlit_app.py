import streamlit as st
from agent import evaluate_use_case
from pathlib import Path
from datetime import datetime
import time 
import html
import markdown as md

def get_references(use_case_text: str):
    text = use_case_text.lower()

    # Core references (always included)
    refs = [
        "NIST AI Risk Management Framework (AI RMF 1.0)",
        "OECD Principles on Artificial Intelligence",
        "ISO/IEC 23894:2023 — AI risk management (overview)",
        "UK ICO — Guidance on AI and data protection (overview)",
    ]

    # Domain add-ons (chosen by simple keyword matching)
    if any(k in text for k in ["hire", "hiring", "resume", "recruit", "candidate", "employment", "hr", "screening"]):
        refs += [
            "U.S. EEOC — Guidance on AI and employment selection procedures (overview)",
            "NYC Local Law 144 (AEDT) — high-level overview (hiring automation)",
        ]

    if any(k in text for k in ["credit", "loan", "underwriting", "lending", "mortgage", "bank", "finance"]):
        refs += [
            "U.S. CFPB — Guidance/updates on algorithmic decision-making (overview)",
            "U.S. FTC — Guidance on AI and consumer protection (overview)",
        ]

    if any(k in text for k in ["patient", "clinical", "hospital", "diagnosis", "medical", "phi", "hipaa", "ehr", "health record", "radiology", "retina"]):
        refs += [
            "HIPAA Privacy Rule — overview (U.S. HHS)",
            "U.S. FDA — AI/ML-enabled medical devices (SaMD) overview",
        ]

    if any(k in text for k in ["child", "children", "minor", "teen", "juvenile", "student", "k-12"]):
        refs += [
            "COPPA — Children’s Online Privacy Protection Act (FTC) overview",
            "U.S. Dept. of Education — Student privacy (FERPA) overview",
        ]

    if any(k in text for k in ["face", "facial", "biometric", "fingerprint", "iris", "surveillance", "camera", "tracking", "location", "gps"]):
        refs += [
            "U.S. FTC — Biometrics and consumer privacy guidance (overview)",
            "State biometrics laws overview (e.g., Illinois BIPA) — high-level summary",
        ]

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for r in refs:
        if r not in seen:
            deduped.append(r)
            seen.add(r)

    return deduped


# Streamlit page config
st.set_page_config(page_title="AI Ethics Agent", layout="centered")
MODEL_NAME = "gpt-4o-mini"
if "step_log" not in st.session_state:
    st.session_state.step_log = []
    
if "report" not in st.session_state:
    st.session_state.report = None

if "plan" not in st.session_state:
    st.session_state.plan = None

if "run_info" not in st.session_state:
    st.session_state.run_info = None
    
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

        # --- References & Further Reading (core + domain add-ons) ---
        references = get_references(user_input)
        markdown_content += "\n---\n\n## References & Further Reading\n"
        for ref in references:
            markdown_content += f"- {ref}\n"
        markdown_content += "\n"

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

        # Build HTML version for download (true rendered HTML)
        html_body = md.markdown(markdown_content, extensions=["extra", "tables"])
        html_report = f"""<!doctype html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>AI Use Case Evaluation Report</title>
        <style>
            body {{ max-width: 900px; margin: 24px auto; padding: 0 16px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }}
            h1, h2, h3 {{ margin-top: 1.2em; }}
            ul {{ margin-top: 0.25em; }}
            hr {{ margin: 24px 0; }}
            code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
        </style>
        </head>
        <body>
        {html_body}
        </body>
        </html>
        """

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





