import { useState } from 'react';
import { Clock, Eye, Share2, BookOpen, TrendingUp, Globe, Leaf, Heart } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Article {
  id: string;
  title: string;
  excerpt: string;
  author: string;
  publishDate: string;
  readTime: string;
  views: number;
  category: string;
  imageUrl: string;
  featured: boolean;
  ecoImpact: string;
  translated: boolean;
}

export function EcoNews() {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const articles: Article[] = [
    {
      id: '1',
      title: 'Revolutionary Ocean Cleanup Technology Removes 100,000kg of Plastic',
      excerpt: 'New breakthrough in marine conservation sees largest plastic removal operation succeed in the Pacific Ocean, offering hope for our seas.',
      author: 'Dr. Marina Chen',
      publishDate: '2024-01-15',
      readTime: '6 min read',
      views: 2847,
      category: 'Ocean Conservation',
      imageUrl: 'https://images.unsplash.com/photo-1708864162641-c748729de0b3?w=800',
      featured: true,
      ecoImpact: 'High Impact',
      translated: false,
    },
    {
      id: '2',
      title: 'Solar Panel Efficiency Breaks 30% Barrier in Laboratory Tests',
      excerpt: 'Scientists achieve new milestone in renewable energy technology, bringing us closer to affordable clean energy for all.',
      author: 'Prof. Ahmed Hassan',
      publishDate: '2024-01-14',
      readTime: '5 min read',
      views: 1923,
      category: 'Renewable Energy',
      imageUrl: 'https://images.unsplash.com/photo-1638068109209-002be3ae4950?w=800',
      featured: true,
      ecoImpact: 'Game Changer',
      translated: true,
    },
    {
      id: '3',
      title: 'Urban Vertical Farms Reduce Water Usage by 95%',
      excerpt: 'Innovative farming techniques in cities are revolutionizing food production while dramatically reducing environmental impact.',
      author: 'Sara Lindgren',
      publishDate: '2024-01-13',
      readTime: '7 min read',
      views: 1456,
      category: 'Sustainable Agriculture',
      imageUrl: 'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800',
      featured: false,
      ecoImpact: 'High Impact',
      translated: false,
    },
    {
      id: '4',
      title: 'Climate Action: How 5 Cities Cut Carbon Emissions by 50%',
      excerpt: 'Learn from the success stories of urban centers leading the fight against climate change through innovative policies and community engagement.',
      author: 'Michael Rodriguez',
      publishDate: '2024-01-12',
      readTime: '8 min read',
      views: 3241,
      category: 'Climate Action',
      imageUrl: 'https://images.unsplash.com/photo-1565011471985-8a450248b005?w=800',
      featured: true,
      ecoImpact: 'Game Changer',
      translated: true,
    },
    {
      id: '5',
      title: 'Biodegradable Packaging From Seaweed Hits Mainstream',
      excerpt: 'Major food brands adopt revolutionary seaweed-based packaging, promising to eliminate millions of tons of plastic waste.',
      author: 'Dr. Emma Thompson',
      publishDate: '2024-01-11',
      readTime: '4 min read',
      views: 987,
      category: 'Sustainable Packaging',
      imageUrl: 'https://images.unsplash.com/photo-1695548487486-3649bfc8dd9a?w=800',
      featured: false,
      ecoImpact: 'High Impact',
      translated: false,
    },
    {
      id: '6',
      title: 'Electric Vehicle Adoption Surpasses 30% in Nordic Countries',
      excerpt: 'Scandinavian nations lead the transition to sustainable transportation, setting an example for global EV adoption.',
      author: 'Lars Peterson',
      publishDate: '2024-01-10',
      readTime: '5 min read',
      views: 2156,
      category: 'Green Transportation',
      imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800',
      featured: false,
      ecoImpact: 'Moderate Impact',
      translated: true,
    },
  ];

  const categories = ['all', 'Climate Action', 'Renewable Energy', 'Ocean Conservation', 'Sustainable Agriculture', 'Green Transportation', 'Sustainable Packaging'];

  const filteredArticles = selectedCategory === 'all' 
    ? articles 
    : articles.filter(article => article.category === selectedCategory);

  const featuredArticles = filteredArticles.filter(article => article.featured);
  const regularArticles = filteredArticles.filter(article => !article.featured);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'Game Changer': return 'bg-green-600 text-white';
      case 'High Impact': return 'bg-blue-600 text-white';
      case 'Moderate Impact': return 'bg-yellow-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  const ArticleCard = ({ article, featured = false }: { article: Article; featured?: boolean }) => (
    <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer ${
      featured ? 'md:col-span-2 ring-2 ring-green-200' : ''
    }`}>
      <div className={`${featured ? 'md:flex' : ''}`}>
        <div className={`${featured ? 'md:w-1/2' : ''} relative`}>
          <ImageWithFallback
            src={article.imageUrl}
            alt={article.title}
            className={`w-full object-cover ${featured ? 'h-48 md:h-full' : 'h-48'}`}
          />
          <div className="absolute top-3 left-3 flex gap-2">
            {featured && (
              <Badge className="bg-green-600">
                <Leaf className="w-3 h-3 mr-1" />
                Featured
              </Badge>
            )}
            <Badge className={getImpactColor(article.ecoImpact)}>
              {article.ecoImpact}
            </Badge>
          </div>
          {article.translated && (
            <Badge className="absolute top-3 right-3 bg-blue-600">
              <Globe className="w-3 h-3 mr-1" />
              AR
            </Badge>
          )}
        </div>
        <CardContent className={`p-6 ${featured ? 'md:w-1/2' : ''}`}>
          <div className="flex items-center space-x-2 mb-3">
            <Badge variant="outline" className="border-green-200 text-green-700">
              {article.category}
            </Badge>
          </div>
          
          <h3 className={`font-semibold mb-2 line-clamp-2 ${featured ? 'text-xl' : 'text-lg'}`}>
            {article.title}
          </h3>
          
          <p className="text-gray-600 mb-4 line-clamp-3">
            {article.excerpt}
          </p>
          
          <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
            <div className="flex items-center space-x-4">
              <span className="font-medium text-green-700">{article.author}</span>
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{article.readTime}</span>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>{article.views.toLocaleString()}</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {new Date(article.publishDate).toLocaleDateString()}
            </span>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm">
                <Heart className="w-4 h-4 mr-1" />
                Save
              </Button>
              <Button variant="ghost" size="sm">
                <Share2 className="w-4 h-4 mr-1" />
                Share
              </Button>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Eco News & Insights</h1>
            <p className="text-gray-600">Stay informed about environmental progress and sustainability breakthroughs</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 mt-4">
          <Badge variant="secondary" className="bg-green-100 text-green-700">
            <Globe className="w-3 h-3 mr-1" />
            Arabic translations available
          </Badge>
          <Badge variant="secondary" className="bg-blue-100 text-blue-700">
            <TrendingUp className="w-3 h-3 mr-1" />
            AI-curated content
          </Badge>
        </div>
      </div>

      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="grid w-full grid-cols-7 overflow-x-auto">
          {categories.map((category) => (
            <TabsTrigger key={category} value={category} className="capitalize text-xs">
              {category === 'all' ? (
                <div className="flex items-center space-x-1">
                  <Globe className="w-3 h-3" />
                  <span>All</span>
                </div>
              ) : (
                category
              )}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Impact Stories */}
      {selectedCategory === 'all' && featuredArticles.length > 0 && (
        <div className="mb-12">
          <div className="flex items-center space-x-2 mb-6">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h2 className="text-xl font-semibold">Impact Stories</h2>
            <Badge className="bg-green-600">Verified Sources</Badge>
          </div>
          <div className="grid gap-6">
            {featuredArticles.map((article) => (
              <ArticleCard key={article.id} article={article} featured />
            ))}
          </div>
        </div>
      )}

      {/* Latest Articles */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-6">
          <BookOpen className="w-5 h-5 text-green-600" />
          <h2 className="text-xl font-semibold">
            {selectedCategory === 'all' ? 'Latest Environmental News' : `${selectedCategory} Updates`}
          </h2>
        </div>
        
        {regularArticles.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {regularArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-500 mb-2">No articles found</h3>
            <p className="text-gray-400">Try selecting a different category</p>
          </div>
        )}
      </div>

      {/* Load More Button */}
      {regularArticles.length > 0 && (
        <div className="text-center">
          <Button variant="outline" size="lg" className="border-green-200 text-green-700 hover:bg-green-50">
            Load More Articles
          </Button>
        </div>
      )}
    </div>
  );
}