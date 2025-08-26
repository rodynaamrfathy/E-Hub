import os
import google.generativeai as genai
from PIL import Image
from ...core.config import Config
from langchain.tools import Tool


class WasteClassifier:
    def __init__(self, temperature: float = 0.0):
        """Initialize the waste classifier with Google Gemini."""
        self.config = Config()
        self.api_key = self.config.GOOGLE_API_KEY
        self.model_name = self.config.classification_model

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Add temperature control
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": temperature}
        )
    
    def _prepare_image(self, image_path: str):
        """
        Prepares the image for classification by opening and resizing it to 200x200.
        """
        img = Image.open(image_path)
        img = img.resize((200, 200))
        return img

    def _classify_internal(self, image_path: str) -> str:
        """Core logic for classification (not exposed directly)."""
        try:
            img = self._prepare_image(image_path)

            prompt = """
            Look at this image carefully and identify the main waste item shown. 
            Return only the most specific and appropriate item name, without explanation. 
            If you cannot identify it, return 'Unclassifiable'.
            """

            response = self.model.generate_content([img, prompt])

            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
            return "Unclassifiable"

        except Exception:
            return "Unclassifiable"

    def classify_waste(self, image_path: str) -> str:
        """Public method exposed to LangChain Tool."""
        return self._classify_internal(image_path)

    def get_tool(self) -> Tool:
        """Return LangChain Tool for integration."""
        return Tool.from_function(
            name="waste_classification",
            description=(
                "Classify a waste item from an image file path into categories "
                "such as Plastic, Paper, Organic, Glass, Metal, or E-waste."
            ),
            func=self.classify_waste
        )
        

# if __name__ == "__main__":

#     classifier = WasteClassifier()
    
#     # Test images
#     test_images = [
#         "agents/waste_mangment_agent/tools/waste_classification/testing_photos/glass.png",
#         "agents/waste_mangment_agent/tools/waste_classification/testing_photos/pizza_box.png", 
#         "agents/waste_mangment_agent/tools/waste_classification/testing_photos/plastic_cup.png",
#         "agents/waste_mangment_agent/tools/waste_classification/testing_photos/tires.png",
#         "agents/waste_mangment_agent/tools/waste_classification/testing_photos/toothbrush.png"
#     ]
    
#     for img_path in test_images:
#         print(f"\n--- Testing {os.path.basename(img_path)} ---")
#         result = classifier.classify_waste(img_path)
#         print("Simple Classification →", result)
