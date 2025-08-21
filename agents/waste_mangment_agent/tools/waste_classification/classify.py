import os
import google.generativeai as genai
from PIL import Image
from ...core.config import Config

class WasteClassifier:
    def __init__(self, temperature: float = 0):
        """Initialize the waste classifier with Google Gemini."""
        self.config = Config()
        self.api_key = self.config.GOOGLE_API_KEY
        self.model_name = self.config.classification_model

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Add temperature control
        self.model = genai.GenerativeModel(
            model_name=self.model_name
        )
    
    def _prepare_image(self, image_path: str):
        """
        Prepares the image for classification by opening and resizing it to 200x200.
        """
        img = Image.open(image_path)
        img = img.resize((200, 200))
        return img

    def classify_waste(self, img):
        """
        Classify a waste item into categories like Plastic, Paper, Organic, Glass, Metal, E-waste, or Unclassifiable.
        Accepts either a path to an image file or a PIL Image object.
        """
        try:
            # Simple prompt for classification
            prompt = """
            Look at this image and classify the item. Return only the item name.
            """

            response = self.model.generate_content([img, prompt])

            # Extract result text
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
            return "Unclassifiable"

        except Exception:
            return "Unclassifiable"
    

            




if __name__ == "__main__":

    classifier = WasteClassifier()
    
    # Test images
    test_images = [
        "agents/waste_mangment_agent/tools/waste_classification/testing_photos/glass.png",
        "agents/waste_mangment_agent/tools/waste_classification/testing_photos/pizza_box.png", 
        "agents/waste_mangment_agent/tools/waste_classification/testing_photos/plastic_cup.png",
        "agents/waste_mangment_agent/tools/waste_classification/testing_photos/tires.png",
        "agents/waste_mangment_agent/tools/waste_classification/testing_photos/toothbrush.png"
    ]
    
    for img_path in test_images:
        print(f"\n--- Testing {os.path.basename(img_path)} ---")
        result = classifier.classify_waste(img_path)
        print("Simple Classification →", result)
