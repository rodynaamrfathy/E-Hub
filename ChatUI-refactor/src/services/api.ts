import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function getStatus() {
  return axios.get(`${API_BASE}/api/status`).then(r => r.data)
}

// Conversations
export async function createConversation(title: string | null = null) {
  const { data } = await axios.post(`${API_BASE}/api/chat/new`, { title })
  return data
}

export async function listConversations() {
  const { data } = await axios.get(`${API_BASE}/api/chat/list`)
  return data
}

export async function deleteConversationApi(convId: string) {
  const { data } = await axios.delete(`${API_BASE}/api/chat/${convId}`)
  return data
}

export async function getConversationHistory(convId: string) {
  const { data } = await axios.get(`${API_BASE}/api/chat/${convId}/history`)
  return data
}

export async function sendMessageApi(convId: string, content: string) {
  const { data } = await axios.post(`${API_BASE}/api/chat/${convId}/send`, { content })
  return data
}

// Images
export async function uploadImageWithMessage(convId: string, file: File, query?: string) {
  const formData = new FormData()
  formData.append('conv_id', convId)
  if (query) formData.append('query', query)
  formData.append('image_file', file)

  const { data } = await axios.post(`${API_BASE}/api/upload/images/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function getImageHistory() {
  const { data } = await axios.get(`${API_BASE}/api/images/images/history`)
  return data
}
