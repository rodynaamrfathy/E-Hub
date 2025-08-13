from langchain_community.document_loaders import PyPDFLoader
import json

# -------- CONFIG --------
pdf_path = "sample.pdf"      # Path to your PDF
output_json = "output.json"  # Where to save the JSON

# -------- LOAD PDF --------
loader = PyPDFLoader(pdf_path)
pages = loader.load()  # List of Document objects (one per page)

# -------- CONVERT TO JSON --------
data = []
for i, page in enumerate(pages, start=1):
    data.append({
        "page_number": i,
        "text": page.page_content.strip()
    })

# -------- SAVE JSON --------
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ PDF converted to JSON and saved to {output_json}")
