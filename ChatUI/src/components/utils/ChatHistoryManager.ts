import { ChatConversation, ChatMessage, FileAttachment, UploadHistoryItem, ChatHistoryManager } from '../types/ChatTypes';

class ChatHistoryService {
  private storageKey = 'dawar-chat-history';
  private uploadStorageKey = 'dawar-upload-history';

  // Load chat history from localStorage
  loadChatHistory(): ChatHistoryManager {
    try {
      const stored = localStorage.getItem(this.storageKey);
      const uploadStored = localStorage.getItem(this.uploadStorageKey);
      
      const conversations = stored ? JSON.parse(stored).map((conv: any) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt),
        messages: conv.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      })) : [];

      const uploadHistory = uploadStored ? JSON.parse(uploadStored).map((item: any) => ({
        ...item,
        uploadedAt: new Date(item.uploadedAt),
        lastUsed: new Date(item.lastUsed),
        file: {
          ...item.file,
          uploadedAt: new Date(item.file.uploadedAt)
        }
      })) : [];

      return {
        conversations,
        uploadHistory,
        currentConversationId: null
      };
    } catch (error) {
      console.error('Failed to load chat history:', error);
      return {
        conversations: [],
        uploadHistory: [],
        currentConversationId: null
      };
    }
  }

  // Save chat history to localStorage
  saveChatHistory(conversations: ChatConversation[]): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }

  // Save upload history to localStorage
  saveUploadHistory(uploadHistory: UploadHistoryItem[]): void {
    try {
      localStorage.setItem(this.uploadStorageKey, JSON.stringify(uploadHistory));
    } catch (error) {
      console.error('Failed to save upload history:', error);
    }
  }

  // Create new conversation
  createConversation(title?: string): ChatConversation {
    const now = new Date();
    return {
      id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: title || `Conversation ${now.toLocaleDateString()}`,
      messages: [{
        id: `msg_${Date.now()}`,
        text: '🌱 Hello! I\'m your DAWAR AI Eco Assistant. How can I help you today? You can also upload PDFs for analysis or images for environmental assessment!',
        sender: 'bot',
        timestamp: now
      }],
      createdAt: now,
      updatedAt: now,
      attachedFiles: []
    };
  }

  // Add message to conversation
  addMessage(conversation: ChatConversation, message: Omit<ChatMessage, 'id' | 'timestamp'>): ChatConversation {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };

    return {
      ...conversation,
      messages: [...conversation.messages, newMessage],
      updatedAt: new Date()
    };
  }

  // Add file to upload history
  addToUploadHistory(file: FileAttachment, conversationId: string): UploadHistoryItem {
    const now = new Date();
    return {
      id: `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      file,
      conversationsUsed: [conversationId],
      uploadedAt: now,
      lastUsed: now
    };
  }

  // Update upload history usage
  updateUploadHistoryUsage(uploadHistory: UploadHistoryItem[], fileId: string, conversationId: string): UploadHistoryItem[] {
    return uploadHistory.map(item => {
      if (item.file.id === fileId) {
        return {
          ...item,
          conversationsUsed: [...new Set([...item.conversationsUsed, conversationId])],
          lastUsed: new Date()
        };
      }
      return item;
    });
  }

  // Generate conversation title from first message
  generateConversationTitle(messages: ChatMessage[]): string {
    const firstUserMessage = messages.find(msg => msg.sender === 'user');
    if (firstUserMessage) {
      const title = firstUserMessage.text.substring(0, 50);
      return title.length === 50 ? title + '...' : title;
    }
    return `Conversation ${new Date().toLocaleDateString()}`;
  }

  // Process PDF file (mock RAG functionality)
  async processPDF(file: File): Promise<string> {
    // Mock PDF processing - in real implementation, this would send to RAG service
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`I've successfully processed your PDF "${file.name}". I can now answer questions about its content related to sustainability, environmental impact, and eco-friendly practices. What would you like to know?`);
      }, 2000);
    });
  }

  // Process image file
  async processImage(file: File): Promise<string> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`I've analyzed your image "${file.name}". I can provide environmental insights, identify sustainability aspects, or suggest eco-friendly improvements. What specific analysis would you like?`);
      }, 1500);
    });
  }
}

export const chatHistoryService = new ChatHistoryService();