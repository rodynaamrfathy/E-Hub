// Conversation types
export interface ConversationCreateDTO {
  title: string | null
}

export interface ConversationResponseDTO {
  conv_id: string
  title: string
  created_at: string
}

export interface ConversationListDTO {
  conv_id: string
  title: string
  updated_at: string
}

// Message types
export interface MessageCreateDTO {
  content: string
}

export interface MessageResponseDTO {
  msg_id: string
  conv_id: string
  sender: string
  content: string
  created_at: string
}

export interface MessageHistoryDTO {
  msg_id: string
  conv_id: string
  role: string
  content: string
  timestamp: string
}

// API Response types
export interface ApiError {
  detail: string
}

export interface DeleteResponse {
  message: string
}
