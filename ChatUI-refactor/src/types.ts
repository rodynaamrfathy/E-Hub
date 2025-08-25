export interface ConversationListDTO {
  conv_id: string
  title: string | null
  updated_at: string
}

export interface ConversationResponseDTO {
  conv_id: string
  title: string | null
  created_at: string
}

export interface MessageResponseDTO {
  msg_id: string
  conv_id: string
  sender: string
  content: string
  created_at: string
}

export interface MessageHistoryDTO {
  role: string
  timestamp: string
  type: string
  content?: string | null
  images?: ImageDTO[] | null
}

export interface ImageDTO {
  image_id: string
  mime_type: string
  image_base64: string
  classification?: ImageClassificationDTO | null
}

export interface ImageClassificationDTO {
  label: string
  recycle_instructions: string
}

export interface ImageHistoryDTO {
  image_id: string
  msg_id: string
  label: string
  recycle_instructions: string
  created_at: string
}
