import { useState } from 'react';
import { EnhancedChatbot } from './components/EnhancedChatbot';
import { MessageCircle } from 'lucide-react';

export default function App() {
  const [showChatbot, setShowChatbot] = useState(true);

  return (
    <div className="min-h-screen bg-[#f6f5f8] flex flex-col relative">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#01a669] rounded-full flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">DAWAR AI Eco Assistant</h1>
              <p className="text-sm text-gray-500">Your sustainability AI companion</p>
            </div>
          </div>
          
          {!showChatbot && (
            <button
              onClick={() => setShowChatbot(true)}
              className="bg-[#01a669] text-white px-4 py-2 rounded-lg hover:bg-[#01a669]/90 transition-colors flex items-center gap-2"
            >
              <MessageCircle className="w-4 h-4" />
              Open Chat
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex items-center justify-center p-4">
        {!showChatbot ? (
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-[#01a669] rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Welcome to DAWAR AI Eco Assistant
            </h2>
            <p className="text-gray-600 mb-6">
              Your intelligent sustainability companion. Get eco-friendly advice, upload documents for analysis, 
              and track your environmental impact with AI-powered insights.
            </p>
            
            <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
              <div className="bg-white p-3 rounded-lg border">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  📄
                </div>
                <p className="font-medium">PDF Analysis</p>
                <p className="text-gray-500 text-xs">Upload sustainability documents</p>
              </div>
              
              <div className="bg-white p-3 rounded-lg border">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  🖼️
                </div>
                <p className="font-medium">Image Assessment</p>
                <p className="text-gray-500 text-xs">Environmental image analysis</p>
              </div>
              
              <div className="bg-white p-3 rounded-lg border">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  💬
                </div>
                <p className="font-medium">Chat History</p>
                <p className="text-gray-500 text-xs">Persistent conversations</p>
              </div>
              
              <div className="bg-white p-3 rounded-lg border">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  🎯
                </div>
                <p className="font-medium">Expert Advice</p>
                <p className="text-gray-500 text-xs">Specialized sustainability help</p>
              </div>
            </div>
            
            <button
              onClick={() => setShowChatbot(true)}
              className="bg-[#01a669] text-white px-6 py-3 rounded-lg hover:bg-[#01a669]/90 transition-colors flex items-center gap-2 mx-auto"
            >
              <MessageCircle className="w-5 h-5" />
              Start Chatting
            </button>
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center text-gray-500">
              <p>Chat interface is open</p>
              <p className="text-sm">Use the chat panel to interact with your AI assistant</p>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Chatbot Component */}
      <EnhancedChatbot showChatbot={showChatbot} setShowChatbot={setShowChatbot} />

      {/* Floating Chat Button (when chat is closed) */}
      {!showChatbot && (
        <button
          onClick={() => setShowChatbot(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-[#01a669] rounded-full shadow-lg z-50 flex items-center justify-center hover:bg-[#01a669]/90 transition-colors"
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </button>
      )}

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto text-center text-sm text-gray-500">
          <p>DAWAR AI-ECO-Knowledge-HUB • Your Sustainability AI Companion</p>
          <p className="text-xs mt-1">
            Features: Chat History • File Upload • PDF Analysis • Image Assessment • Expert Guidance
          </p>
        </div>
      </div>
    </div>
  );
}