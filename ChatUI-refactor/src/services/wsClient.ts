// src/api/wsClient.ts
let socket: WebSocket | null = null

export function connectWebSocket(onMessage: (msg: any) => void) {
  socket = new WebSocket("ws://127.0.0.1:8000/ws/chat") // 🔗 update for prod

  socket.onopen = () => {
    console.log("✅ WebSocket connected")
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch {
      console.error("❌ Invalid WS message:", event.data)
    }
  }

  socket.onclose = () => {
    console.log("⚠️ WebSocket closed")
  }

  socket.onerror = (err) => {
    console.error("❌ WebSocket error", err)
  }
}

export function sendTextMessage(text: string) {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ text }))
  }
}

export function sendImageMessage(file: File, query?: string) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return

  const reader = new FileReader()
  reader.onload = () => {
    const base64Data = (reader.result as string).split(",")[1]
    socket!.send(
      JSON.stringify({
        text: query || "",
        images: [{ data: base64Data, mime_type: file.type }]
      })
    )
  }
  reader.readAsDataURL(file)
}
