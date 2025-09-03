import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_gemini_model():
    """Initialize the Gemini model with streaming enabled"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",  # You can use "gemini-pro" or other models
        temperature=0.7,
        max_output_tokens=1000,
        google_api_key=os.getenv("GOOGLE_API_KEY"),  # Set GOOGLE_API_KEY in your .env file
        # streaming is enabled by default in LangChain
    )
    return llm

def stream_gemini_response():
    """Demonstrate basic streaming functionality"""
    llm = setup_gemini_model()
    
    # Create the message prompt
    messages = [
        SystemMessage(content="You are a helpful assistant that provides concise answers."),
        HumanMessage(content="Explain the concept of quantum computing in simple terms.")
    ]
    
    print("Starting streaming response...\n")
    print("Response: ", end="", flush=True)
    
    # Stream the response
    for chunk in llm.stream(messages):
        if hasattr(chunk, 'content'):
            print(chunk.content, end="", flush=True)  # Print without newline
    
    print("\n\nStreaming complete!")

if __name__ == "__main__":
    stream_gemini_response()