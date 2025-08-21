import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Leaf, MessageCircle, HelpCircle, FileText, Target } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  suggestions?: string[];
}

export function EcoAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '🌱 Hello! I\'m your DAWAR AI Eco Assistant. How can I help you today? Choose from the options below or ask me anything about sustainability!',
      sender: 'bot',
      timestamp: new Date(),
      suggestions: ['Tell me about renewable energy', 'How to reduce plastic waste', 'Carbon footprint tips', 'Sustainable living guide']
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickActions = [
    { icon: FileText, label: 'Summarization', action: 'summarization' },
    { icon: HelpCircle, label: 'Q&A', action: 'qa' },
    { icon: MessageCircle, label: 'Chat', action: 'chat' },
    { icon: Target, label: 'TopicSpecific', action: 'topic' },
  ];

  const handleQuickAction = (action: string) => {
    const actionMessages: { [key: string]: string } = {
      summarization: 'Please provide a summary of the latest sustainability trends',
      qa: 'I have questions about environmental topics',
      chat: 'Let\'s have a conversation about eco-friendly practices',
      topic: 'I need specific information about a sustainability topic'
    };
    
    setInputValue(actionMessages[action]);
    setTimeout(() => handleSendMessage(actionMessages[action]), 100);
  };

  const handleSendMessage = async (customMessage?: string) => {
    const messageText = customMessage || inputValue;
    if (!messageText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: getBotResponse(messageText),
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500);
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
    } else if (input.includes('plastic') || input.includes('waste')) {
      return '🌊 Great question about reducing plastic waste!\n\n• Use reusable water bottles and shopping bags\n• Choose products with minimal packaging\n• Buy in bulk to reduce packaging waste\n• Switch to bamboo or metal alternatives\n• Properly sort recyclables\n\n💡 Small changes make a big impact! Would you like specific recommendations for plastic-free alternatives?';
    } else if (input.includes('energy') || input.includes('electricity')) {
      return '⚡ Here are some effective energy-saving tips:\n\n🏠 At Home:\n• Use LED bulbs (75% less energy)\n• Unplug electronics when not in use\n• Set thermostat 2°F lower in winter\n• Use cold water for washing clothes\n• Seal air leaks around windows/doors\n\n📊 These changes can reduce your energy bill by 10-25%! Want help calculating your potential savings?';
    } else if (input.includes('transport') || input.includes('car') || input.includes('travel')) {
      return '🚲 Sustainable transportation options:\n\n🌿 Daily Commute:\n• Walk or bike for trips under 2 miles\n• Use public transportation\n• Carpool or use ride-sharing\n• Work from home when possible\n• Consider electric or hybrid vehicles\n\n✈️ For longer trips:\n• Train travel over flying when possible\n• Combine multiple errands in one trip\n• Plan staycations to explore locally\n\nEvery mile saved prevents ~1 lb of CO2! Ready to plan your eco-friendly route?';
    } else if (input.includes('recycle') || input.includes('recycling')) {
      return '♻️ Recycling made simple:\n\n✅ Always Recyclable:\n• Paper, cardboard, glass bottles\n• Aluminum cans, plastic bottles (#1-2)\n• Steel/tin cans\n\n❌ Not Recyclable:\n• Plastic bags (return to store drop-off)\n• Styrofoam, broken glass\n• Food-contaminated items\n\n🏠 Pro tip: Clean containers before recycling and check your local guidelines. Need help finding recycling centers near you?';
    } else if (input.includes('renewable') || input.includes('solar') || input.includes('wind')) {
      return '🔋 **Renewable Energy Overview**\n\n☀️ **Solar Power**:\n• Cost decreased 70% in past decade\n• Home solar can reduce electricity bills by 90%\n• Payback period: 6-10 years\n\n💨 **Wind Energy**:\n• Fastest growing energy source globally\n• Offshore wind capacity expanding rapidly\n• Can power entire communities\n\n🌊 **Other Renewables**:\n• Hydroelectric: Reliable baseload power\n• Geothermal: Consistent 24/7 generation\n• Biomass: Waste-to-energy solutions\n\nInterested in residential solar or community renewable programs?';
    } else if (input.includes('hello') || input.includes('hi')) {
      return '🌱 Hello there! I\'m excited to help you on your sustainability journey. I can provide:\n\n• Personalized eco-friendly tips\n• Carbon footprint reduction strategies\n• Recycling and waste management guidance\n• Sustainable lifestyle recommendations\n• Topic-specific environmental information\n\nWhat aspect of sustainable living interests you most?';
    } else {
      return '🤔 That\'s a great question! I\'m here to help with all things sustainability.\n\nI can assist you with:\n🌿 Environmental topics and solutions\n♻️ Waste reduction and recycling\n⚡ Energy efficiency and renewable energy\n🚲 Sustainable transportation and lifestyle\n📊 Summarizing environmental trends\n❓ Answering specific eco questions\n\nTry using the quick action buttons above, or tell me more about what you\'d like to learn!';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    setTimeout(() => handleSendMessage(suggestion), 100);
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
            <Leaf className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold">DAWAR AI Eco Assistant</h2>
            <p className="text-green-100">Your personal sustainability guide</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Button
                key={action.action}
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction(action.action)}
                className="flex items-center space-x-2"
              >
                <Icon className="w-4 h-4 text-green-600" />
                <span>{action.label}</span>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 px-6 py-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id}>
              <div
                className={`flex items-start space-x-3 ${
                  message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' ? 'bg-blue-500' : 'bg-green-500'
                }`}>
                  {message.sender === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Leaf className="w-4 h-4 text-white" />
                  )}
                </div>
                
                <div className={`max-w-xs lg:max-w-2xl ${
                  message.sender === 'user' ? 'text-right' : ''
                }`}>
                  <div className={`rounded-lg px-4 py-3 ${
                    message.sender === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <p className="whitespace-pre-line">{message.text}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
              
              {/* Suggestions */}
              {message.suggestions && (
                <div className="mt-3 ml-11 flex flex-wrap gap-2">
                  {message.suggestions.map((suggestion, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="cursor-pointer hover:bg-green-100 hover:text-green-700"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isTyping && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <Leaf className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex space-x-3">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about sustainability, request summaries, or explore specific topics..."
            className="flex-1"
            disabled={isTyping}
          />
          <Button 
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isTyping}
            size="sm"
            className="bg-green-600 hover:bg-green-700"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}