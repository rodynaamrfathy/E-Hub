import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

class StreamingChatBot:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.chat_history = []
        
        # System prompt
        self.system_message = SystemMessage(
            content="You are a helpful, friendly assistant. Provide clear and concise answers."
        )
    
    def chat_stream(self, user_input):
        """Stream chat response while maintaining conversation history"""
        # Add user message to history
        self.chat_history.append(HumanMessage(content=user_input))
        
        # Prepare all messages (system + history)
        all_messages = [self.system_message] + self.chat_history
        
        print("\nAssistant: ", end="", flush=True)
        full_response = ""
        
        # Stream the response
        for chunk in self.llm.stream(all_messages):
            if hasattr(chunk, 'content'):
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
        
        # Add AI response to history
        self.chat_history.append(AIMessage(content=full_response))
        
        return full_response
    
    def run_chat_interface(self):
        """Interactive chat interface with streaming"""
        print("Welcome to the Gemini Streaming Chat!")
        print("Type 'quit' to exit the chat.\n")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                self.chat_stream(user_input)
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")

# Environment setup instructions
def setup_instructions():
    print("""
    SETUP INSTRUCTIONS:
    1. Create a .env file in your project directory
    2. Add your Google API key: GOOGLE_API_KEY=your_actual_api_key_here
    3. Install required packages:
       pip install langchain-google-genai python-dotenv langchain-core
    4. Enable the Gemini API in your Google Cloud Console
    """)

if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY not found in environment variables.")
        setup_instructions()
    else:
        bot = StreamingChatBot()
        bot.run_chat_interface()