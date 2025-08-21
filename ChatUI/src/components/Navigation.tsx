import { useState } from 'react';
import { MessageSquare, Newspaper, User, Menu, X, ShoppingBag, BarChart3 } from 'lucide-react';
import { Button } from './ui/button';
import dawarIcon from 'figma:asset/7950f49cfe6712782eba74cc0dba1e1b95fa0dfd.png';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const tabs = [
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
    { id: 'news', label: 'Eco Hub', icon: Newspaper },
    { id: 'marketplace', label: 'Marketplace', icon: ShoppingBag },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'account', label: 'Profile', icon: User },
  ];

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between w-full max-w-7xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center">
              <img src={dawarIcon} alt="DAWAR" className="w-10 h-10 rounded-xl" />
            </div>
            <div>
              <span className="text-xl font-bold text-gray-900">DAWAR</span>
              <p className="text-xs text-[#01A669] font-medium">AI-ECO-Knowledge-HUB</p>
            </div>
          </div>
          
          <div className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? "default" : "ghost"}
                  onClick={() => onTabChange(tab.id)}
                  className="flex items-center space-x-2 px-4 py-2"
                  style={{
                    backgroundColor: activeTab === tab.id ? '#01A669' : undefined,
                    color: activeTab === tab.id ? 'white' : undefined
                  }}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </Button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Mobile Navigation */}
      <nav className="md:hidden bg-white border-b border-gray-200">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center">
              <img src={dawarIcon} alt="DAWAR" className="w-8 h-8 rounded-lg" />
            </div>
            <div>
              <span className="text-lg font-bold text-gray-900">DAWAR</span>
              <p className="text-xs text-[#01A669] font-medium">AI-ECO-HUB</p>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>
        </div>
        
        {isMobileMenuOpen && (
          <div className="border-t border-gray-200 px-4 py-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? "default" : "ghost"}
                  onClick={() => {
                    onTabChange(tab.id);
                    setIsMobileMenuOpen(false);
                  }}
                  className="w-full justify-start flex items-center space-x-2 px-3 py-2 mb-1"
                  style={{
                    backgroundColor: activeTab === tab.id ? '#01A669' : undefined,
                    color: activeTab === tab.id ? 'white' : undefined
                  }}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </Button>
              );
            })}
          </div>
        )}
      </nav>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2 z-50">
        <div className="flex justify-around">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant="ghost"
                onClick={() => onTabChange(tab.id)}
                className={`flex flex-col items-center space-y-1 px-2 py-2 ${
                  activeTab === tab.id ? 'text-[#01A669]' : 'text-gray-500'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-xs">{tab.label}</span>
              </Button>
            );
          })}
        </div>
      </div>
    </>
  );
}