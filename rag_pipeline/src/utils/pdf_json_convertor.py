from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import json

def pdf_to_json(pdf_path, output_dir="json/files/"):
    try:
        # -------- CONFIG --------
        pdf_path = Path(pdf_path)      # Path to your PDF
        output_dir = Path(output_dir)  # Directory for JSON output
        output_dir.mkdir(parents=True, exist_ok=True)  # Create dir if it doesn't exist

        # Generate JSON file name based on PDF name
        output_json = output_dir / f"{pdf_path.stem}.json"

        # -------- LOAD PDF --------
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        # -------- CONVERT TO JSON --------
        data = [
            {
                "page_number": i,
                "text": page.page_content.strip()
            }
            for i, page in enumerate(pages, start=1)
        ]

        # -------- CHECK IF EMPTY --------
        if not data or all(not page["text"] for page in data):
            raise ValueError("❌ PDF has no extractable text. JSON is empty.")

        # -------- SAVE JSON --------
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"✅ PDF converted to JSON and saved to {output_json}")
        
        return data 

    except Exception as e:
        print(f"❌ Error converting PDF to JSON: {e}")
        return []
