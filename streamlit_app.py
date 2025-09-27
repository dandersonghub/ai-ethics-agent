import streamlit as st
from agent import evaluate_use_case
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# Streamlit page config
st.set_page_config(page_title="AI Ethics Agent", layout="centered")
st.title("🛡️ AI Ethics Agent")
st.markdown("""
Use this tool to **evaluate your AI use case** across key ethical risk categories:
- **Bias**
- **Privacy**
- **Explainability**
- **Governance & Oversight**

💡 Understanding these areas is critical before deploying any AI solution — especially for systems that impact real people. This tool helps uncover ethical risks you may not have considered.
  
_One report is generated per use case and downloadable as a Word document (.docx)._""")

# Input box
user_input = st.text_area(
    "Describe your AI use case:",
    placeholder="E.g. An AI model that predicts hospital readmission using patient records, deployed on cloud...",
    height=200,
    key="use_case_input"
)

if st.button("Evaluate Use Case"):
    if not user_input.strip():
        st.warning("Please enter a description before submitting.")
    else:
        progress = st.progress(0, text="Evaluating ethical risks...")

        results = evaluate_use_case(user_input)

        progress.progress(100, text="✅ Evaluation complete!")

        # Build Markdown-style string for report
        markdown_content = f"# AI Use Case Evaluation Report\n\n**Use Case:**\n{user_input.strip()}\n\n"
        for key, value in results.items():
            markdown_content += f"## {key}\n{value.strip()}\n\n"

        # Save Markdown file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        md_path = reports_dir / f"eval_{timestamp}.md"
        docx_path = reports_dir / f"eval_{timestamp}.docx"
        md_path.write_text(markdown_content, encoding="utf-8")

        # Convert to polished .docx
        doc = Document()
        styles = doc.styles
        normal_style = styles["Normal"].font
        normal_style.name = "Calibri"
        normal_style.size = Pt(11)

        doc.add_heading("AI Use Case Evaluation Report", level=1)
        p = doc.add_paragraph()
        p.add_run("Use Case: ").bold = True
        p.add_run(user_input.strip())

        for category, explanation in results.items():
            doc.add_heading(category, level=2)
            for line in explanation.strip().split("\n"):
                if line.strip().startswith("•") or line.strip().startswith("-"):
                    para = doc.add_paragraph(style='List Bullet')
                    para.add_run(line.strip()[1:].strip())
                elif line.strip().startswith("**") and line.strip().endswith("**"):
                    para = doc.add_paragraph()
                    para.add_run(line.strip().strip("**")).bold = True
                elif line.strip().startswith("**"):
                    parts = line.strip().split("**")
                    para = doc.add_paragraph()
                    para.add_run(parts[1]).bold = True
                    para.add_run(parts[2] if len(parts) > 2 else "")
                else:
                    doc.add_paragraph(line.strip())

        doc.save(docx_path)

        # Display report
        st.subheader("✅ Evaluation Results")
        st.markdown(markdown_content)

        # Download button for .docx
        with open(docx_path, "rb") as f:
            st.download_button("📄 Download Word Report (.docx)", f, file_name=docx_path.name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # Clear input box
        st.session_state.use_case_input = ""
