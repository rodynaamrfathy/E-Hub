from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import asyncio
import json
import os
from typing import AsyncGenerator

# Initialize FastAPI app
app = FastAPI(title="LangChain Gemini Streaming API")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 1000

# Initialize Gemini LLM
def get_llm(temperature: float = 0.7, max_tokens: int = 1000):
    """Initialize the Gemini LLM with LangChain"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GOOGLE_API_KEY environment variable not set"
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # or "gemini-1.5-pro"
        temperature=temperature,
        max_tokens=max_tokens,
        google_api_key=api_key
    )

async def generate_stream_response(message: str, temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    """Generate streaming response from Gemini via LangChain"""
    try:
        llm = get_llm(temperature, max_tokens)
        
        # Create a human message
        human_message = HumanMessage(content=message)
        
        # Stream the response
        async for chunk in llm.astream([human_message]):
            if chunk.content:
                # Format as Server-Sent Events
                data = {
                    "content": chunk.content,
                    "done": False
                }
                yield f"data: {json.dumps(data)}\n\n"
        
        # Send completion signal
        final_data = {
            "content": "",
            "done": True
        }
        yield f"data: {json.dumps(final_data)}\n\n"
        
    except Exception as e:
        error_data = {
            "error": str(e),
            "done": True
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LangChain Gemini Streaming API is running!"}

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response from Gemini"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    return StreamingResponse(
        generate_stream_response(request.message, request.temperature, request.max_tokens),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint for comparison"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        llm = get_llm(request.temperature, request.max_tokens)
        human_message = HumanMessage(content=request.message)
        
        response = await llm.ainvoke([human_message])
        return {"response": response.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)