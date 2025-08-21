import { useState } from 'react';
import { Search, Heart, Share, Bookmark, MessageCircle, Send } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { CategoryFilter } from './CategoryFilter';
import { NewsDetail } from './NewsDetail';
import imgRectangle14133 from "figma:asset/9ac84c9d1b286f35e6ad14c1e4e0aa8eee84ca60.png";
import imgRectangle14649 from "figma:asset/6f912f61fc514121723535e9f9280bf42af62727.png";
import imgRound from "figma:asset/fe972e7c3ed82d24359608b42a06e4d999447de9.png";
import imgRound1 from "figma:asset/55dd5e6fe21e09ab93f81724147063a9f70952b5.png";

interface NewsItem {
  id: string;
  title: string;
  category: string;
  date: string;
  author: string;
  authorImage: string;
  image: string;
  likes: number;
  excerpt: string;
}

export function EcoHubIntegrated() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedNews, setSelectedNews] = useState<string | null>(null);
  const [showChatbot, setShowChatbot] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { id: '1', text: 'Hello! How can I help you with sustainability today?', sender: 'bot' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const newsItems: NewsItem[] = [
    {
      id: '1',
      title: '10 Simple Ways to Reduce Plastic Waste',
      category: 'tutorials',
      date: 'Oct 20, 2025',
      author: 'Nestlé',
      authorImage: imgRound,
      image: imgRectangle14133,
      likes: 363,
      excerpt: 'Practical tips for reducing plastic waste in your daily life'
    },
    {
      id: '2',
      title: '5 Easy Ways to Reduce Your Carbon Footprint',
      category: 'tutorials',
      date: 'Nov 20, 2025',
      author: 'Pepsi',
      authorImage: imgRound1,
      image: imgRectangle14649,
      likes: 285,
      excerpt: 'Simple lifestyle changes that make a big environmental impact'
    },
    {
      id: '3',
      title: 'Green Technology Innovations',
      category: 'news',
      date: 'Dec 15, 2025',
      author: 'EcoTech',
      authorImage: imgRound,
      image: imgRectangle14133,
      likes: 412,
      excerpt: 'Latest breakthroughs in sustainable technology'
    }
  ];

  const filteredNews = activeCategory === 'all' 
    ? newsItems 
    : newsItems.filter(item => item.category === activeCategory);

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    
    const newMessage = {
      id: Date.now().toString(),
      text: chatInput,
      sender: 'user'
    };
    
    setChatMessages(prev => [...prev, newMessage]);
    setChatInput('');
    
    // Simulate bot response
    setTimeout(() => {
      setChatMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: "That's a great question! I can help you with eco-friendly tips and sustainability advice.",
        sender: 'bot'
      }]);
    }, 1000);
  };

  if (selectedNews) {
    return <NewsDetail onBack={() => setSelectedNews(null)} />;
  }

  return (
    <div className="min-h-screen bg-white relative">
      {/* Header */}
      <div className="px-4 py-6 border-b border-gray-100">
        <h1 className="text-2xl font-bold text-black">Eco Hub</h1>
      </div>

      {/* Featured Article */}
      <div className="px-4 py-6">
        <div 
          onClick={() => setSelectedNews('1')}
          className="relative rounded-xl overflow-hidden cursor-pointer"
        >
          <img 
            src={imgRectangle14133} 
            alt="Featured article"
            className="w-full h-48 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-4 left-4 right-4">
            <h2 className="text-white text-lg font-bold mb-2">
              10 Simple Ways to Reduce Plastic Waste
            </h2>
            <div className="flex items-center gap-2 mb-3">
              <img src={imgRound} alt="Nestlé" className="w-6 h-6 rounded-full" />
              <span className="text-white text-sm">Nestlé</span>
            </div>
            <div className="bg-[#01A669] text-white px-3 py-1 rounded-full text-sm font-medium inline-block">
              Tutorials
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="px-4 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <Input 
            placeholder="Search...." 
            className="pl-10 bg-[#f6f5f8] border-none rounded-2xl"
          />
        </div>
      </div>

      {/* Category Filter */}
      <CategoryFilter 
        activeCategory={activeCategory} 
        onCategoryChange={setActiveCategory} 
      />

      {/* News List */}
      <div className="px-4 space-y-4 pb-20">
        {filteredNews.map((item) => (
          <div 
            key={item.id}
            onClick={() => setSelectedNews(item.id)}
            className="bg-white rounded-xl border border-gray-100 p-4 cursor-pointer hover:shadow-sm transition-shadow"
          >
            <div className="flex gap-4">
              <img 
                src={item.image} 
                alt={item.title}
                className="w-24 h-24 rounded-lg object-cover flex-shrink-0"
              />
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-black text-base leading-tight mb-2">
                  {item.title}
                </h3>
                <div className="flex items-center gap-2 mb-2">
                  <img src={item.authorImage} alt={item.author} className="w-4 h-4 rounded-full" />
                  <span className="text-gray-500 text-xs">{item.author}</span>
                  <span className="text-gray-300">•</span>
                  <span className="text-gray-500 text-xs">{item.date}</span>
                </div>
                <p className="text-gray-500 text-xs mb-3">{item.category}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Heart className="w-3 h-3 text-gray-400" />
                    <span className="text-gray-400 text-xs">{item.likes}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Bookmark className="w-3 h-3 text-gray-400" />
                    <Share className="w-3 h-3 text-gray-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Floating Chat Button */}
      <Button
        onClick={() => setShowChatbot(!showChatbot)}
        className="fixed bottom-20 right-4 w-14 h-14 rounded-full bg-[#01A669] hover:bg-[#01A669]/90 shadow-lg z-50"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </Button>

      {/* Chatbot Overlay */}
      {showChatbot && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
          <div className="bg-white w-full h-2/3 rounded-t-2xl flex flex-col">
            <div className="bg-[#01A669] text-white p-4 rounded-t-2xl flex justify-between items-center">
              <h3 className="font-semibold">Eco Assistant</h3>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowChatbot(false)}
                className="text-white hover:bg-white/20"
              >
                ×
              </Button>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {chatMessages.map((message) => (
                <div 
                  key={message.id} 
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`px-3 py-2 rounded-lg max-w-xs ${
                      message.sender === 'user' 
                        ? 'bg-[#01A669] text-white' 
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {message.text}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask me about sustainability..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSendMessage}
                  className="bg-[#01A669] hover:bg-[#01A669]/90"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}