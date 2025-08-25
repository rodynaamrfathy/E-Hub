export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  attachments?: FileAttachment[];
}

export interface FileAttachment {
  id: string;
  name: string;
  type: 'image';
  size: number;
  url: string;
  uploadedAt: Date;
}

export interface ChatConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  attachedFiles: FileAttachment[];
}

export interface UploadHistoryItem {
  id: string;
  file: FileAttachment;
  conversationsUsed: string[];
  uploadedAt: Date;
  lastUsed: Date;
}

export interface ChatHistoryManager {
  conversations: ChatConversation[];
  uploadHistory: UploadHistoryItem[];
  currentConversationId: string | null;
}