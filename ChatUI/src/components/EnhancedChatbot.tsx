import { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, FileText, HelpCircle, Target, Upload, X, File, Image, History, Paperclip, Trash2 } from 'lucide-react';
import { ChatConversation, ChatMessage, FileAttachment, UploadHistoryItem } from './types/ChatTypes';
import { chatHistoryService } from './utils/ChatHistoryManager';

interface EnhancedChatbotProps {
  showChatbot: boolean;
  setShowChatbot: (show: boolean) => void;
}

export function EnhancedChatbot({ showChatbot, setShowChatbot }: EnhancedChatbotProps) {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [uploadHistory, setUploadHistory] = useState<UploadHistoryItem[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ChatConversation | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [showUploadHistory, setShowUploadHistory] = useState(false);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [isBotLoading, setIsBotLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  // Load chat history on component mount
  useEffect(() => {
    const historyManager = chatHistoryService.loadChatHistory();
    setConversations(historyManager.conversations);
    setUploadHistory(historyManager.uploadHistory);

    // If no conversations exist, create a new one
    if (historyManager.conversations.length === 0) {
      const newConv = chatHistoryService.createConversation();
      setConversations([newConv]);
      setCurrentConversation(newConv);
    } else {
      // Set the most recent conversation as current
      const latest = historyManager.conversations.sort((a, b) => 
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )[0];
      setCurrentConversation(latest);
    }
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);

  // Save conversations when they change
  useEffect(() => {
    if (conversations.length > 0) {
      chatHistoryService.saveChatHistory(conversations);
    }
  }, [conversations]);

  // Save upload history when it changes
  useEffect(() => {
    if (uploadHistory.length > 0) {
      chatHistoryService.saveUploadHistory(uploadHistory);
    }
  }, [uploadHistory]);


  const handleSendMessage = async (customMessage?: string) => {
    const messageText = customMessage || chatInput;
    if (!messageText.trim() || !currentConversation) return;

    // Add user message
    const updatedConversation = chatHistoryService.addMessage(currentConversation, {
      text: messageText,
      sender: 'user'
    });

    setCurrentConversation(updatedConversation);
    updateConversationInList(updatedConversation);
    setChatInput('');

    // Backend integration: send message to API and get bot response
    setIsBotLoading(true);
    try {
      // Replace with your backend API call
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, conversationId: updatedConversation.id })
      });
      const data = await response.json();
      const botResponse = data.reply || 'Sorry, no response from backend.';
      const finalConversation = chatHistoryService.addMessage(updatedConversation, {
        text: botResponse,
        sender: 'bot'
      });
      setCurrentConversation(finalConversation);
      updateConversationInList(finalConversation);
    } catch (error) {
      const errorConversation = chatHistoryService.addMessage(updatedConversation, {
        text: '❌ Error communicating with backend.',
        sender: 'bot'
      });
      setCurrentConversation(errorConversation);
      updateConversationInList(errorConversation);
    } finally {
      setIsBotLoading(false);
    }
  };

  const updateConversationInList = (updatedConv: ChatConversation) => {
    setConversations(prev => prev.map(conv => 
      conv.id === updatedConv.id ? updatedConv : conv
    ));
  };

  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('summarization') || input.includes('summary') || input.includes('trends')) {
      return '📊 **Latest Sustainability Trends Summary**\n\n🔋 **Renewable Energy**: Solar and wind power costs have dropped 70% in the past decade\n\n🌊 **Ocean Conservation**: New technologies removing millions of tons of plastic from oceans\n\n🏠 **Green Buildings**: LEED-certified buildings reduce energy consumption by 30-50%\n\n🚗 **Electric Mobility**: EV adoption growing 40% annually in key markets\n\n🌱 **Circular Economy**: Companies adopting waste-to-resource models\n\nWould you like me to elaborate on any of these trends?';
    } else if (input.includes('q&a') || input.includes('questions') || input.includes('environmental topics')) {
      return '❓ **Environmental Q&A Mode Activated**\n\nI\'m ready to answer your environmental questions! Here are some popular topics:\n\n🌍 **Climate Change**: Causes, effects, and solutions\n♻️ **Recycling & Waste**: Best practices and local guidelines\n🌿 **Sustainable Living**: Daily habits and lifestyle changes\n🏭 **Corporate Sustainability**: Business environmental practices\n🌱 **Green Technology**: Latest innovations and applications\n\nWhat would you like to know more about? Ask me anything!';
    } else if (input.includes('chat') || input.includes('conversation') || input.includes('eco-friendly practices')) {
      return '💬 **Let\'s Chat About Sustainability!**\n\nI love discussing eco-friendly practices! Here are some conversation starters:\n\n🌟 **Personal Impact**: What small changes have you made recently?\n🏡 **Home & Garden**: Tips for sustainable living spaces\n🍽️ **Food Choices**: Plant-based options and local sourcing\n🚲 **Transportation**: Eco-friendly commuting alternatives\n👕 **Sustainable Fashion**: Ethical clothing and circular fashion\n\nWhat aspect of sustainable living interests you most? I\'d love to hear about your journey and share some insights!';
    } else if (input.includes('topic') || input.includes('specific information') || input.includes('sustainability topic')) {
      return '🎯 **Topic-Specific Information**\n\nI can provide detailed information on specific sustainability topics. Choose an area:\n\n🌊 **Water Conservation**: Techniques, technologies, and impact\n⚡ **Energy Efficiency**: Home and business optimization\n🌱 **Carbon Footprint**: Calculation, reduction strategies\n🏭 **Industrial Ecology**: Circular economy and clean production\n🌿 **Biodiversity**: Conservation and ecosystem protection\n🚛 **Supply Chain**: Sustainable sourcing and logistics\n\nWhich topic would you like to explore in depth? I can provide comprehensive information, current statistics, and actionable steps.';
    } else {
      return '🤔 That\'s a great question! I\'m here to help with all things sustainability.\n\nI can assist you with:\n🌿 Environmental topics and solutions\n♻️ Waste reduction and recycling\n⚡ Energy efficiency and renewable energy\n🚲 Sustainable transportation and lifestyle\n📊 Summarizing environmental trends\n❓ Answering specific eco questions\n📄 Analyzing uploaded PDFs for sustainability insights\n🖼️ Reviewing images for environmental assessment\n\nTry using the quick action buttons above, upload a file, or tell me more about what you\'d like to learn!';
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0 || !currentConversation) return;

    setIsProcessingFile(true);

    for (const file of Array.from(files)) {
      // Validate file type
      const isValidPDF = file.type === 'application/pdf';
      const isValidImage = file.type.startsWith('image/');
      
      if (!isValidPDF && !isValidImage) {
        alert(`${file.name} is not a supported file type. Please upload PDF or image files only.`);
        continue;
      }

      // Create file attachment
      const attachment: FileAttachment = {
        id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        type: isValidPDF ? 'pdf' : 'image',
        size: file.size,
        url: URL.createObjectURL(file),
        uploadedAt: new Date()
      };

      // Add user message with attachment
      const userMessage = chatHistoryService.addMessage(currentConversation, {
        text: `📎 Uploaded: ${file.name}`,
        sender: 'user',
        attachments: [attachment]
      });

      setCurrentConversation(userMessage);
      updateConversationInList(userMessage);

      // Add to upload history
      const uploadItem = chatHistoryService.addToUploadHistory(attachment, currentConversation.id);
      setUploadHistory(prev => [uploadItem, ...prev]);

      // Process file and add bot response
      try {
        let processingResponse: string;
        if (isValidPDF) {
          processingResponse = await chatHistoryService.processPDF(file);
        } else {
          processingResponse = await chatHistoryService.processImage(file);
        }

        const botResponse = chatHistoryService.addMessage(userMessage, {
          text: processingResponse,
          sender: 'bot'
        });

        setCurrentConversation(botResponse);
        updateConversationInList(botResponse);
      } catch (error) {
        const errorResponse = chatHistoryService.addMessage(userMessage, {
          text: `❌ Sorry, I encountered an error processing ${file.name}. Please try again or contact support if the issue persists.`,
          sender: 'bot'
        });

        setCurrentConversation(errorResponse);
        updateConversationInList(errorResponse);
      }
    }

    setIsProcessingFile(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const startNewConversation = () => {
    const newConv = chatHistoryService.createConversation();
    setConversations(prev => [newConv, ...prev]);
    setCurrentConversation(newConv);
    setShowHistory(false);
  };

  const selectConversation = (conversation: ChatConversation) => {
    setCurrentConversation(conversation);
    setShowHistory(false);
  };

  const deleteConversation = (conversationId: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== conversationId));
    if (currentConversation?.id === conversationId) {
      const remaining = conversations.filter(conv => conv.id !== conversationId);
      if (remaining.length > 0) {
        setCurrentConversation(remaining[0]);
      } else {
        const newConv = chatHistoryService.createConversation();
        setConversations([newConv]);
        setCurrentConversation(newConv);
      }
    }
  };

  const reuseUploadedFile = (uploadItem: UploadHistoryItem) => {
    if (!currentConversation) return;

    // Add user message with reused file
    const userMessage = chatHistoryService.addMessage(currentConversation, {
      text: `📎 Reused file: ${uploadItem.file.name}`,
      sender: 'user',
      attachments: [uploadItem.file]
    });

    setCurrentConversation(userMessage);
    updateConversationInList(userMessage);

    // Update upload history
    const updatedHistory = chatHistoryService.updateUploadHistoryUsage(
      uploadHistory, 
      uploadItem.file.id, 
      currentConversation.id
    );
    setUploadHistory(updatedHistory);

    // Add bot response
    setTimeout(() => {
      const botResponse = chatHistoryService.addMessage(userMessage, {
        text: `✅ I've loaded the ${uploadItem.file.type === 'pdf' ? 'PDF document' : 'image'} "${uploadItem.file.name}" from your upload history. I can continue our previous analysis or provide new insights. What would you like to know?`,
        sender: 'bot'
      });

      setCurrentConversation(botResponse);
      updateConversationInList(botResponse);
    }, 500);

    setShowUploadHistory(false);
  };

  if (!showChatbot) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
      <div className="bg-white w-full h-2/3 rounded-t-2xl flex flex-col">
        {/* Header */}
        <div className="bg-[#01a669] text-white p-4 rounded-t-2xl flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">Eco Assistant</h3>
            {currentConversation && (
              <span className="text-xs opacity-75">
                {currentConversation.messages.length - 1} messages
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setShowUploadHistory(!showUploadHistory)}
              className="text-white hover:bg-white/20 w-8 h-8 rounded flex items-center justify-center"
              title="Upload History"
            >
              <Upload className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setShowHistory(!showHistory)}
              className="text-white hover:bg-white/20 w-8 h-8 rounded flex items-center justify-center"
              title="Chat History"
            >
              <History className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setShowChatbot(false)}
              className="text-white hover:bg-white/20 w-8 h-8 rounded flex items-center justify-center"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Chat History Panel */}
        {showHistory && (
          <div className="bg-gray-50 border-b border-gray-200 max-h-48 overflow-y-auto">
            <div className="p-3">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-medium text-gray-800">Chat History</h4>
                <button 
                  onClick={startNewConversation}
                  className="bg-[#01a669] text-white px-3 py-1 rounded text-xs"
                >
                  New Chat
                </button>
              </div>
              <div className="space-y-2">
                {conversations.map(conv => (
                  <div 
                    key={conv.id}
                    className={`p-2 rounded cursor-pointer text-sm ${
                      currentConversation?.id === conv.id 
                        ? 'bg-[#01a669] text-white' 
                        : 'bg-white hover:bg-gray-100'
                    }`}
                    onClick={() => selectConversation(conv)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{conv.title}</p>
                        <p className="text-xs opacity-75">
                          {conv.messages.length - 1} messages • {new Date(conv.updatedAt).toLocaleDateString()}
                        </p>
                      </div>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteConversation(conv.id);
                        }}
                        className="ml-2 p-1 hover:bg-red-100 rounded"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Upload History Panel */}
        {showUploadHistory && (
          <div className="bg-gray-50 border-b border-gray-200 max-h-48 overflow-y-auto">
            <div className="p-3">
              <h4 className="font-medium text-gray-800 mb-3">Upload History</h4>
              <div className="space-y-2">
                {uploadHistory.map(item => (
                  <div 
                    key={item.id}
                    className="bg-white p-2 rounded cursor-pointer text-sm hover:bg-gray-100"
                    onClick={() => reuseUploadedFile(item)}
                  >
                    <div className="flex items-center gap-2">
                      {item.file.type === 'pdf' ? (
                        <File className="w-4 h-4 text-red-500" />
                      ) : (
                        <Image className="w-4 h-4 text-blue-500" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{item.file.name}</p>
                        <p className="text-xs text-gray-500">
                          Used in {item.conversationsUsed.length} conversation(s) • 
                          Last used: {new Date(item.lastUsed).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {uploadHistory.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No files uploaded yet
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        
        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3">
          {currentConversation?.messages.map((message) => (
            <div 
              key={message.id} 
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`px-3 py-2 rounded-lg max-w-xs ${
                  message.sender === 'user' 
                    ? 'bg-[#01a669] text-white' 
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="whitespace-pre-line text-sm">{message.text}</p>
                {message.attachments && message.attachments.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.attachments.map(attachment => (
                      <div key={attachment.id} className="flex items-center gap-2 text-xs opacity-75">
                        {attachment.type === 'pdf' ? (
                          <File className="w-3 h-3" />
                        ) : (
                          <Image className="w-3 h-3" />
                        )}
                        <span>{attachment.name}</span>
                      </div>
                    ))}
                  </div>
                )}
                <p className="text-xs opacity-50 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {isProcessingFile && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-lg">
                <p className="text-sm">🔄 Processing your file...</p>
              </div>
            </div>
          )}
          {isBotLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-lg">
                <p className="text-sm">🤖 Bot is thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,image/*"
              multiple
              onChange={handleFileUpload}
              className="hidden"
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg"
              disabled={isProcessingFile}
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask me about sustainability or upload files..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
              disabled={isProcessingFile}
            />
            <button 
              onClick={() => handleSendMessage()}
              className="bg-[#01a669] hover:bg-[#01a669]/90 text-white px-4 py-2 rounded-lg"
              disabled={isProcessingFile || !chatInput.trim()}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}