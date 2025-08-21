import os
from google import genai
import base64
import os
from google import genai
from google.genai import types

from ...core.config import Config

class WasteClassifier:
    def __init__(self):
        """Initialize the waste classifier with Google Gemini client."""
        
        self.client = genai.Client(api_key=self.api_key)
        self.config = Config()
        self.api_key = self.config.GOOGLE_API_KEY
        selfmodel = self.config.classification_model

    def classify(self, input_text: str = None, image_path: str = None) -> str:
        """
        Classify waste based on text or image.
        - input_text: a description of the item (e.g., 'plastic bottle')
        - image_path: optional image file path for classification
        """
        parts = []
        if input_text:
            parts.append(Part.from_text(text=input_text))

        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            parts.append(
                Part.from_bytes(
                    data=img_bytes,
                    mime_type="image/png",  
                )
            )

        contents = [
            Content(
                role="user",
                parts=parts,
            ),
        ]

        tools = [
            Tool(googleSearch=GoogleSearch())
        ]

        config = GenerateContentConfig(
            thinking_config=ThinkingConfig(thinking_budget=-1),
            tools=tools,
        )

        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                response_text += chunk.text

        return response_text.strip()

if __name__ == "__main__":
    classifier = WasteClassifier()

    # Example 1: Text classification
    result = classifier.classify(input_text="agents/waste_mangment_agent/tools/waste_classification/testing_photos/glass.png")
    print("Text Classification:", result)

    # Example 2: Image classification
    result = classifier.classify(image_path="agents/waste_mangment_agent/tools/waste_classification/testing_photos/tires.png")
    print("Image Classification:", result)
