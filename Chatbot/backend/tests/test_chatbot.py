from services.conversation.GeminiMultimodalChatbot import GeminiMultimodalChatbot
import os
import re

def extract_image_paths(text):
    """Extract valid image paths from user input, removing quotes and apostrophes"""
    # Look for common path patterns with image extensions
    patterns = [
        r"['\"]([^'\"]*\.(?:png|jpg|jpeg|gif|webp))['\"]",  # Quoted paths
        r"(/[^\s]*\.(?:png|jpg|jpeg|gif|webp))",           # Unix absolute paths
        r"([A-Za-z]:[^\s]*\.(?:png|jpg|jpeg|gif|webp))",   # Windows paths
        r"([\w./\\-]+\.(?:png|jpg|jpeg|gif|webp))"         # General paths
    ]
    
    found_paths = []
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        found_paths.extend(matches)
    
    # Clean and validate paths
    valid_paths = []
    for path in found_paths:
        cleaned_path = path.strip("'\"")
        if os.path.isfile(cleaned_path):
            valid_paths.append(cleaned_path)
            print(f"📁 Found valid image: {cleaned_path}")
    
    return valid_paths

def interactive_mode():
    """Run chatbot interactively from terminal"""
    print("Gemini Multimodal Chatbot (Interactive Mode)")
    print("=" * 50)
    
    chatbot = GeminiMultimodalChatbot()
    print(f"✅ Chatbot initialized with session ID: {chatbot.session_id}")
    
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue

            # Extract image paths from input
            images = extract_image_paths(user_input)
            
            # Remove the file paths from the text to avoid confusion
            clean_text = user_input
            for img_path in images:
                clean_text = clean_text.replace(f"'{img_path}'", "").replace(f'"{img_path}"', "").replace(img_path, "")
            clean_text = clean_text.strip()
            
            # If no meaningful text remains after removing paths, use a default question
            if not clean_text or len(clean_text.split()) < 2:
                if images:
                    clean_text = "Can you help me identify this waste item and tell me how to recycle it in Egypt?"
                else:
                    clean_text = user_input  

            print("🤖 Assistant: ", end="", flush=True)
            
            # Pass cleaned text and images to chatbot
            result = chatbot.get_response(clean_text, images if images else None)
            
            if result["success"]:
                print(result["response"])

            else:
                print(f"❌ Error: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    interactive_mode()