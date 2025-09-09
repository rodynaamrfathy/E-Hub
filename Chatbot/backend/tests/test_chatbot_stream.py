from services.conversation.GeminiMultimodalChatbot import GeminiMultimodalChatbot
import os
import re
import asyncio


def extract_image_paths(text):
    """Extract valid image paths from user input, removing quotes and apostrophes"""
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
    
    valid_paths = []
    for path in found_paths:
        cleaned_path = path.strip("'\"")
        if os.path.isfile(cleaned_path):
            valid_paths.append(cleaned_path)
            print(f"📁 Found valid image: {cleaned_path}")
    
    return valid_paths


async def interactive_mode():
    """Run chatbot interactively with streaming output"""
    print("Gemini Multimodal Chatbot (Streaming Mode)")
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
            
            # Clean input text (remove paths)
            clean_text = user_input
            for img_path in images:
                clean_text = clean_text.replace(f"'{img_path}'", "").replace(f'"{img_path}"', "").replace(img_path, "")
            clean_text = clean_text.strip()
            
            if not clean_text or len(clean_text.split()) < 2:
                if images:
                    clean_text = "Can you help me identify this waste item and tell me how to recycle it in Egypt?"
                else:
                    clean_text = user_input  

            print("🤖 Assistant: ", end="", flush=True)

            # Stream tokens as they come in
            async for token in chatbot.stream_response(clean_text, images if images else None):
                print(token, end="", flush=True)

            # Print final newline after streaming is done
            print("\n" + "-" * 50)
            print(f"📜 Full response: {chatbot.get_full_response()}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(interactive_mode())
