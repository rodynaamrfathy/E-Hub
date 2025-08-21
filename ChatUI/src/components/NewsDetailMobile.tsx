import { ArrowLeft, Heart, Share, Bookmark } from 'lucide-react';
import imgRectangle14133 from "figma:asset/9ac84c9d1b286f35e6ad14c1e4e0aa8eee84ca60.png";
import imgRound from "figma:asset/fe972e7c3ed82d24359608b42a06e4d999447de9.png";

interface NewsDetailMobileProps {
  newsId: string | null;
  onBack: () => void;
}

export function NewsDetailMobile({ newsId, onBack }: NewsDetailMobileProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="relative">
        <img 
          src={imgRectangle14133} 
          alt="Article cover" 
          className="w-full h-64 object-cover"
        />
        
        {/* Header overlay with controls */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
          <button 
            onClick={onBack}
            className="bg-black/20 text-white hover:bg-black/40 rounded-full w-10 h-10 flex items-center justify-center"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className="flex gap-2">
            <button className="bg-black/20 text-white hover:bg-black/40 rounded-full w-10 h-10 flex items-center justify-center">
              <Heart className="w-5 h-5" />
            </button>
            <button className="bg-black/20 text-white hover:bg-black/40 rounded-full w-10 h-10 flex items-center justify-center">
              <Bookmark className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Date overlay */}
        <div className="absolute bottom-4 left-4">
          <div className="bg-[#01a669] text-white px-3 py-1 rounded-full text-sm font-medium">
            Tutorials
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        <div className="text-sm text-gray-500 mb-2 text-[#8b8b8b]">Oct 20, 2025</div>
        
        <h1 className="text-2xl font-bold text-black mb-4 leading-tight">
          10 Simple Ways to Reduce Plastic Waste
        </h1>

        <div className="flex items-center gap-3 mb-6">
          <img 
            src={imgRound} 
            alt="Nestlé" 
            className="w-8 h-8 rounded-full"
          />
          <span className="text-gray-600 text-sm">Nestlé</span>
        </div>

        <div className="prose max-w-none">
          <p className="text-gray-800 leading-relaxed mb-4 text-[16px]">
            Plastic pollution is one of the biggest environmental challenges of our time, but 
            small everyday actions can make a big difference. From carrying a reusable bag and 
            water bottle to avoiding single-use packaging, everyone can take simple steps 
            to reduce plastic waste.
          </p>
          
          <p className="text-gray-800 leading-relaxed mb-4 text-[16px]">
            Making conscious choices not only helps protect our oceans and wildlife but also 
            encourages a more sustainable lifestyle. Plastic pollution is one of the biggest 
            environmental challenges of our time, but small everyday actions can make a big 
            difference. From carrying a reusable bag and water bottle to avoiding single-use 
            packaging, everyone can take simple steps to reduce plastic waste.
          </p>

          <h3 className="text-lg font-semibold text-black mt-6 mb-3">Key Strategies</h3>
          
          <ul className="space-y-2 text-gray-800 text-[16px] mb-4">
            <li>• Use reusable water bottles and shopping bags</li>
            <li>• Choose products with minimal packaging</li>
            <li>• Buy in bulk to reduce packaging waste</li>
            <li>• Switch to bamboo or metal alternatives</li>
            <li>• Properly sort recyclables</li>
          </ul>

          <p className="text-gray-800 leading-relaxed mt-4 text-[16px]">
            Small changes make a big impact! By implementing these simple strategies, 
            we can collectively work towards a more sustainable future and help protect 
            our planet for generations to come.
          </p>
        </div>

        {/* Bottom actions */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 text-gray-600 hover:text-[#01a669]">
              <Heart className="w-4 h-4" />
              <span className="text-sm">363</span>
            </button>
          </div>
          
          <button className="text-gray-600 hover:text-[#01a669]">
            <Share className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Bottom spacing for mobile */}
      <div className="h-20" />
    </div>
  );
}