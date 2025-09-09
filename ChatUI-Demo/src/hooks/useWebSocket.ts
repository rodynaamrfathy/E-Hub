// hooks/useWebSocket.ts
import { useEffect, useRef } from "react"

type WSMessage = {
  event: string
  [key: string]: any
}

export function useWebSocket(
  onMessage: (msg: WSMessage) => void,
  url: string = "ws://localhost:8000/ws"
) {
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    ws.current = new WebSocket(url)

    ws.current.onopen = () => {
      console.log("✅ WS connected:", url)
    }

    ws.current.onmessage = (e) => {
      try {
        const data: WSMessage = JSON.parse(e.data)
        onMessage(data)
      } catch (err) {
        console.error("WS parse error:", err)
      }
    }

    ws.current.onclose = () => {
      console.log("❌ WS closed")
    }

    return () => ws.current?.close()
  }, [onMessage, url])

  // Send JSON messages
  function send(event: string, payload: any) {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ event, ...payload }))
    }
  }

  // Send image (base64 or ArrayBuffer)
  function sendImage(event: string, file: File) {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return
    const reader = new FileReader()
    reader.onload = () => {
      ws.current?.send(
        JSON.stringify({
          event,
          filename: file.name,
          type: file.type,
          data: reader.result, // base64 string
        })
      )
    }
    reader.readAsDataURL(file)
  }

  return { send, sendImage }
}
