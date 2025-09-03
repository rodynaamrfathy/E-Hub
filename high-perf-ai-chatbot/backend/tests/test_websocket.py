import asyncio
import websockets
import json
import base64

def encode_image_to_base64(path: str, mime_type="image/jpeg") -> dict:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return {"data": data, "mime_type": mime_type}

async def chat():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        print("Connected ✅. Type your message and press Enter. Type 'exit' to quit.\n")

        while True:
            user_input = input("🧑 You: ")
            if user_input.lower() in {"exit", "quit"}:
                print("Closing chat...")
                break

            payload = None
            # If user types "upload <file_path>"
            if user_input.startswith("upload "):
                path = user_input.replace("upload ", "").strip()
                try:
                    image_payload = [encode_image_to_base64(path)]
                    payload = {"text": "Please analyze this image", "images": image_payload}
                except FileNotFoundError:
                    print(f"❌ File not found: {path}")
                    continue
            else:
                payload = {"text": user_input}

            await websocket.send(json.dumps(payload))

            while True:
                response = await websocket.recv()
                if response == "[DONE]":
                    break
                print("🤖 Assistant:", response)

asyncio.run(chat())
