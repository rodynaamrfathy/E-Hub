import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class GeminiStreamer:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    def stream_with_stats(self, prompt):
        """Stream response with timing and token statistics"""
        messages = [HumanMessage(content=prompt)]
        
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        start_time = time.time()
        full_response = ""
        chunk_count = 0
        
        print("Streaming response: ", end="", flush=True)
        
        # Process each chunk
        for chunk in self.llm.stream(messages):
            chunk_count += 1
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)
                full_response += chunk.content
            
            # Simulate some processing on each chunk
            self._process_chunk(chunk, chunk_count)
        
        end_time = time.time()
        
        print(f"\n\n{'='*50}")
        print(f"Streaming completed in {end_time - start_time:.2f} seconds")
        print(f"Received {chunk_count} chunks")
        print(f"Final response length: {len(full_response)} characters")
        
        return full_response
    
    def _process_chunk(self, chunk, chunk_number):
        """Custom processing for each chunk (can be extended)"""
        # You can add custom logic here, such as:
        # - Sentiment analysis on the fly
        # - Content filtering
        # - Real-time translation
        # - Progress tracking
        
        # Simple example: print chunk metadata occasionally
        if chunk_number % 5 == 0:
            if hasattr(chunk, 'response_metadata'):
                print(f"\n[Chunk {chunk_number} metadata received]", end="", flush=True)
    
    def async_stream_example(self, prompt):
        """Example of asynchronous streaming"""
        import asyncio
        
        async def async_stream():
            messages = [HumanMessage(content=prompt)]
            print(f"Async streaming: {prompt}")
            
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    print(chunk.content, end="", flush=True)
            
            print("\nAsync streaming complete!")
        
        return asyncio.run(async_stream())

# Usage examples
def main():
    streamer = GeminiStreamer()
    
    # Example 1: Basic streaming
    print("=== BASIC STREAMING EXAMPLE ===")
    streamer.stream_with_stats("What are the benefits of renewable energy?")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Creative writing with streaming
    print("=== CREATIVE WRITING STREAMING ===")
    creative_prompt = """Write a short story about a robot who discovers emotions. 
    Make it engaging and include a twist at the end."""
    
    streamer.stream_with_stats(creative_prompt)
    
    # Example 3: Code explanation with streaming
    print("\n" + "="*60 + "\n")
    print("=== CODE EXPLANATION STREAMING ===")
    code_prompt = "Explain how Python's list comprehensions work with examples."
    
    streamer.stream_with_stats(code_prompt)

if __name__ == "__main__":
    main()