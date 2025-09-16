import os
import google.generativeai as genai
import numpy as np
import time
from dotenv import load_dotenv

load_dotenv()
class embedder:
    def __init__(self):
        """Initialize the processor with API configuration."""
        self.api_key = os.getenv("GOOGLE_API_KEY_MM")
        genai.configure(api_key=self.api_key)
        self.model = "models/gemini-embedding-exp-03-07"


    def get_embeddings(self, texts):
        """Get embeddings for a list of texts."""
        embeddings = []    
        for i, text in enumerate(texts):
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=768
                )
                if "embedding" in response:
                    embeddings.append(response["embedding"])
                if i < len(texts) - 1:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error processing text {i + 1}: {e}")
                continue
        
        return np.array(embeddings)

