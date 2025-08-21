import { useState } from 'react';
import { Search, Heart, Share, Bookmark, MessageCircle, ArrowLeft } from 'lucide-react';
import { EnhancedChatbot } from './EnhancedChatbot';
import svgPaths from "../imports/svg-cuqvvrfxbt";
import imgRectangle14133 from "figma:asset/9ac84c9d1b286f35e6ad14c1e4e0aa8eee84ca60.png";
import imgFade from "figma:asset/5f83d134db05f20a13db07d29cfc9582a22a91a6.png";
import imgRound from "figma:asset/fe972e7c3ed82d24359608b42a06e4d999447de9.png";
import imgRectangle14649 from "figma:asset/6f912f61fc514121723535e9f9280bf42af62727.png";
import imgRound1 from "figma:asset/55dd5e6fe21e09ab93f81724147063a9f70952b5.png";
import imgHome11 from "figma:asset/f4329d247d71e05d6e27b2122a3ef6197581ca99.png";
import imgWorld11 from "figma:asset/c905fd32fc4c9c16c2b4334506a667f0b1efe48b.png";
import imgPollH1 from "figma:asset/ce6ff786eb835d0b4497b9f76f9b5dc1e2f4f90b.png";
import img5 from "figma:asset/c121adc2bb31818dff375f4df326be985b22a96e.png";

interface EcoHubMobileProps {
  onNavigate: (view: string) => void;
  onNewsSelect: (newsId: string) => void;
}

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

export function EcoHubMobile({ onNavigate, onNewsSelect }: EcoHubMobileProps) {
  const [activeCategory, setActiveCategory] = useState('all');
  const [showChatbot, setShowChatbot] = useState(false);

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

  const categories = [
    { id: 'all', label: 'All' },
    { id: 'news', label: 'News' },
    { id: 'articles', label: 'Articles' },
    { id: 'tutorials', label: 'Tutorials' },
    { id: 'events', label: 'Events' },
  ];

  const filteredNews = activeCategory === 'all' 
    ? newsItems 
    : newsItems.filter(item => item.category === activeCategory);

  return (
    <div className="bg-[#ffffff] relative min-h-screen">
      {/* Status Bar */}
      <div className="absolute bottom-[94.62%] left-0 overflow-clip right-0 top-0">
        <div className="absolute h-[21px] rounded-3xl top-3.5 translate-x-[-50%] w-[54px]" style={{ left: "calc(16.667% - 11px)" }}>
          <div className="absolute font-['Poppins:SemiBold',_sans-serif] h-5 leading-[0] left-[27px] not-italic text-[#000000] text-[17px] text-center top-px tracking-[-0.408px] translate-x-[-50%] w-[54px]">
            <p className="block leading-[22px]">9:41</p>
          </div>
        </div>
        
        {/* Battery, WiFi, Signal icons */}
        <div className="absolute contents top-[19px] translate-x-[-50%]" style={{ left: "calc(83.333% - 0.299px)" }}>
          <div className="absolute h-[13px] top-[19px] translate-x-[-50%] w-[27.401px]" style={{ left: "calc(83.333% + 24.701px)" }}>
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 13">
              <g>
                <path d={svgPaths.p2a8e2e00} opacity="0.35" stroke="black" strokeWidth="1.05509" />
                <path d={svgPaths.p5fdc300} fill="black" opacity="0.4" />
                <path d={svgPaths.p2748c800} fill="black" />
              </g>
            </svg>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="px-4 py-6 pt-20 border-b border-gray-100">
        <h1 className="text-2xl font-bold text-black text-center">Eco Hub</h1>
      </div>

      {/* Featured Article */}
      <div className="px-4 py-6">
        <div 
          onClick={() => onNewsSelect('1')}
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
            <div className="bg-[#01a669] text-white px-3 py-1 rounded-full text-sm font-medium inline-block">
              Tutorials
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="px-4 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input 
            placeholder="Search...." 
            className="w-full pl-10 pr-4 py-3 bg-[#f6f5f8] border-none rounded-2xl text-[14px]"
          />
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex gap-3 px-4 py-4 overflow-x-auto">
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setActiveCategory(category.id)}
            className={`px-4 py-2 rounded-2xl text-sm font-medium whitespace-nowrap transition-colors ${
              activeCategory === category.id
                ? 'bg-[#01a669] text-white font-semibold'
                : 'bg-[#f6f5f8] text-[#8e8e8e] hover:bg-gray-200'
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* News List */}
      <div className="px-4 space-y-4 pb-24">
        {filteredNews.map((item) => (
          <div 
            key={item.id}
            onClick={() => onNewsSelect(item.id)}
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

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40">
        <div className="flex justify-around py-2">
          <button 
            onClick={() => onNavigate('home')}
            className="flex flex-col items-center py-2 text-[#b8b8b8]"
          >
            <img src={imgHome11} alt="Home" className="w-6 h-6" />
            <span className="text-xs mt-1">Home</span>
          </button>
          
          <button className="flex flex-col items-center py-2 text-[#b8b8b8]">
            <img src={imgPollH1} alt="Requests" className="w-6 h-6" />
            <span className="text-xs mt-1">Requests</span>
          </button>
          
          <button className="flex flex-col items-center py-2 text-[#01a669]">
            <img src={imgWorld11} alt="Eco Hub" className="w-6 h-6" />
            <span className="text-xs mt-1">Eco Hub</span>
          </button>
          
          <button className="flex flex-col items-center py-2 text-[#b8b8b8]">
            <img src={img5} alt="Rewards" className="w-6 h-6" />
            <span className="text-xs mt-1">Rewards</span>
          </button>
          
          <button className="flex flex-col items-center py-2 text-[#b8b8b8]">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinejoin="round" strokeWidth="2" d="M16.1245 6.75C15.9408 9.22828 14.062 11.25 11.9995 11.25C9.93705 11.25 8.05502 9.22875 7.87455 6.75C7.68705 4.17188 9.51517 2.25 11.9995 2.25C14.4839 2.25 16.312 4.21875 16.1245 6.75Z" />
              <path strokeWidth="2" d="M12 14.25C7.92187 14.25 3.78281 16.5 3.01687 20.7469C2.92453 21.2587 3.21422 21.75 3.75 21.75H20.25C20.7863 21.75 21.0759 21.2587 20.9836 20.7469C20.2172 16.5 16.0781 14.25 12 14.25Z" />
            </svg>
            <span className="text-xs mt-1">Profile</span>
          </button>
        </div>
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setShowChatbot(!showChatbot)}
        className="fixed bottom-20 right-4 w-14 h-14 rounded-full bg-[#01a669] hover:bg-[#01a669]/90 shadow-lg z-50 flex items-center justify-center"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </button>

      {/* Enhanced Chatbot Component */}
      <EnhancedChatbot showChatbot={showChatbot} setShowChatbot={setShowChatbot} />
    </div>
  );
}