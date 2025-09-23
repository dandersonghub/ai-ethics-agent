import os
from datetime import datetime
from agent import evaluate_use_case

print("Welcome to the AI Ethics Assistant Agent!")
user_input = input("Please describe your AI use case (e.g. what data it uses, where it's deployed, who it affects):\n\nYour description: ")

# Run evaluation
results = evaluate_use_case(user_input)

# Format Markdown report
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
report_filename = f"report_{timestamp}.md"
report_path = os.path.join("reports", report_filename)

markdown_lines = [
    "# 🧠 AI Ethics Evaluation Report",
    f"**Timestamp:** `{timestamp}`",
    "",
    "## 📄 Use Case Description",
    user_input,
    ""
]

for category, evaluation in results.items():
    markdown_lines.append(f"## 🔍 {category.capitalize()}")
    markdown_lines.append(evaluation)
    markdown_lines.append("")  # For spacing

# Save to .md file
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(markdown_lines))

print(f"\n✅ Report saved to `{report_path}`")
