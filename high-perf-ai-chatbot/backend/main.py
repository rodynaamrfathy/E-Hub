from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.websocket import stream_gemini_to_websocket

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            await stream_gemini_to_websocket(websocket, data)
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/status")
async def get_api_status():
    return {
        "api_status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "chat": True,
            "image_upload": True,
            "image_classification": True,
            "conversation_history": True,
            "export_data": True
        },
        "ai_services": {
            "gemini_chatbot": True,
            "waste_management_agent": True
        }
    }