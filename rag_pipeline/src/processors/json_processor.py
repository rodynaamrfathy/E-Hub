import rag_pipeline.src.processors.base_preprocessor as BasePreprocessor 
import json
from langchain.schema import Document
import logging
import rag_pipeline.src.utils.pdf_json_convertor as pdf_loader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JSONPreprocessor(BasePreprocessor.BasePreprocessor):
    def load_and_preprocess_data(self, file_path):
        raw_data=pdf_loader.pdf_to_json(file_path)
        if not raw_data:
            logger.warning(f"No data found in {file_path}. Returning empty string.")
            return ""
        clean_texts = [self.clean_text(entry["text"]) for entry in raw_data if isinstance(entry, dict)]
        return "\n".join(clean_texts)
    def process_documents_from_files(self, file_paths):
        documents = []
        for i, file_path in enumerate(file_paths):
            text = self.load_and_preprocess_data(file_path).strip()
            documents.append(
                Document(page_content=text, metadata={"pdf_id": i})
            )
        return documents
