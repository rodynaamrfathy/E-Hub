from ..services.conversation.multimodal_chatbot import GeminiMultimodalChatbot
import os
import re

def extract_image_paths(text):
    """Extract valid image paths from user input"""
    potential_paths = re.findall(
        r'[\w./\\-]+\.(?:png|jpg|jpeg|gif|webp)', text, flags=re.IGNORECASE
    )
    return [p for p in potential_paths if os.path.isfile(p)]

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

            # Detect image paths in input
            images = extract_image_paths(user_input)

            print("🤖 Assistant: ", end="", flush=True)
            result = chatbot.get_response(user_input, images if images else None)
            
            if result["success"]:
                print(result["response"])
                if result.get("web_search_used"):
                    print("🔎 (Web search results were included)")
            else:
                print(f"❌ Error: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def batch_test_mode():
    """Run chatbot on all test images inside a folder"""
    print("Gemini Multimodal Chatbot (Batch Test Mode)")
    print("=" * 50)

    chatbot = GeminiMultimodalChatbot()
    print(f"✅ Chatbot ready (Session ID: {chatbot.session_id})")

    # Folder containing test images
    folder = "agents/waste_mangment_agent/tools/waste_classification/testing_photos"
    
    if not os.path.exists(folder):
        print(f"❌ Test folder not found: {folder}")
        return

    image_files = [
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    ]

    if not image_files:
        print("⚠️ No images found in test folder.")
        return

    for img in image_files:
        print(f"\n🖼️ Testing {img}...")
        
        text = (
            "Classify this waste item in the image. "
            "Explain how it can be recycled or reused, "
            "and mention relevant recycling initiatives or organizations in Egypt."
        )
        
        response = chatbot.get_response(text, [img])
        
        if response["success"]:
            print("🤖", response["response"])
            if response.get("web_search_used"):
                print("🔎 (Web search results were included)")
        else:
            print(f"❌ Error: {response['error']}")


if __name__ == "__main__":

    interactive_mode()
