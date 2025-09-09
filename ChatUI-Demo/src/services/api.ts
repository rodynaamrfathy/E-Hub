import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function getStatus() {
  return axios.get(`${API_BASE}/api/status`).then(r => r.data)
}

// Conversations
export async function createConversation(title: string | null = null) {
  const { data } = await axios.post(`${API_BASE}/chat/new`, { title })
  return data
}

export async function listConversations() {
  const { data } = await axios.get(`${API_BASE}/chat/list`)
  return data
}

export async function deleteConversationApi(convId: string) {
  const { data } = await axios.delete(`${API_BASE}/chat/${convId}`)
  return data
}

export async function getConversationHistory(convId: string) {
  const { data } = await axios.get(`${API_BASE}/chat/${convId}/history`)
  return data
}

// Updated streaming function to match backend expectations
export function sendMessageStream(
  convId: string, 
  content: string, 
  images: File[] | null = null,
  onToken: (token: string) => void, 
  onComplete: () => void, 
  onError: (error: string) => void
) {
  const controller = new AbortController()
  
  // Create FormData to match backend endpoint
  const formData = new FormData()
  formData.append('content', content)
  
  // Add images if provided
  if (images && images.length > 0) {
    images.forEach(image => {
      formData.append('images', image)
    })
  }
  
  fetch(`${API_BASE}/chat/${convId}/send-stream`, {
    method: 'POST',
    body: formData, // Use FormData instead of JSON
    signal: controller.signal
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No response body')
    }
  
    const decoder = new TextDecoder()
    let buffer = ''
  
    function readStream(): Promise<void> {
      return reader.read().then(({ done, value }) => {
        if (done) {
          console.log('Stream completed')
          onComplete()
          return
        }
  
        const chunk = decoder.decode(value, { stream: true })
        console.log('Received chunk:', chunk)
        buffer += chunk
        
        // Process complete lines
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.trim() === '') continue // Skip empty lines
          
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            console.log('Processing data:', data)
            
            if (data === '[DONE]') {
              console.log('Stream finished')
              onComplete()
              return
            }
            
            try {
              const parsed = JSON.parse(data)
              console.log('Parsed token:', parsed)
              if (parsed.token) {
                onToken(parsed.token)
              } else if (parsed.error) {
                onError(parsed.error)
                return
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, 'Data:', data)
            }
          }
        }
        
        return readStream()
      })
    }
    
    return readStream()
  })
  .catch(error => {
    console.error('Fetch error:', error)
    if (error.name !== 'AbortError') {
      onError(error.message)
    }
  })
  
  return {
    abort: () => controller.abort()
  }
}

// Remove the separate image upload function since it's now integrated into sendMessageStream
// The backend only has the /send-stream endpoint for handling both text and images