import { useState } from 'react';
import { Clock, Eye, Share2, BookOpen, TrendingUp, Globe } from 'lucide-react';
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
}

export function NewsSection() {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const articles: Article[] = [
    {
      id: '1',
      title: 'The Future of Digital Transformation in 2024',
      excerpt: 'Exploring the latest trends and technologies shaping businesses worldwide, from AI integration to cloud computing innovations.',
      author: 'Sarah Johnson',
      publishDate: '2024-01-15',
      readTime: '5 min read',
      views: 1234,
      category: 'Technology',
      imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800',
      featured: true,
    },
    {
      id: '2',
      title: 'Global Economic Outlook: What Experts Predict',
      excerpt: 'Leading economists share their insights on market trends, inflation patterns, and growth forecasts for the coming year.',
      author: 'Michael Chen',
      publishDate: '2024-01-14',
      readTime: '7 min read',
      views: 892,
      category: 'Business',
      imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
      featured: false,
    },
    {
      id: '3',
      title: 'Sustainable Energy Solutions Making an Impact',
      excerpt: 'Discover how renewable energy technologies are revolutionizing power generation and reducing environmental impact.',
      author: 'Emily Rodriguez',
      publishDate: '2024-01-13',
      readTime: '6 min read',
      views: 567,
      category: 'Environment',
      imageUrl: 'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800',
      featured: false,
    },
    {
      id: '4',
      title: 'Healthcare Innovation: AI-Powered Diagnostics',
      excerpt: 'How artificial intelligence is transforming medical diagnosis and improving patient outcomes across healthcare systems.',
      author: 'Dr. James Wilson',
      publishDate: '2024-01-12',
      readTime: '8 min read',
      views: 1456,
      category: 'Health',
      imageUrl: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800',
      featured: true,
    },
    {
      id: '5',
      title: 'Remote Work Culture: Building Team Connection',
      excerpt: 'Best practices for maintaining team cohesion and productivity in distributed work environments.',
      author: 'Lisa Park',
      publishDate: '2024-01-11',
      readTime: '4 min read',
      views: 723,
      category: 'Workplace',
      imageUrl: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800',
      featured: false,
    },
    {
      id: '6',
      title: 'Cybersecurity Trends: Protecting Digital Assets',
      excerpt: 'Essential strategies for safeguarding business data and systems against emerging cyber threats.',
      author: 'Alex Thompson',
      publishDate: '2024-01-10',
      readTime: '6 min read',
      views: 945,
      category: 'Technology',
      imageUrl: 'https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=800',
      featured: false,
    },
  ];

  const categories = ['all', 'Technology', 'Business', 'Health', 'Environment', 'Workplace'];

  const filteredArticles = selectedCategory === 'all' 
    ? articles 
    : articles.filter(article => article.category === selectedCategory);

  const featuredArticles = articles.filter(article => article.featured);
  const regularArticles = filteredArticles.filter(article => !article.featured);

  const ArticleCard = ({ article, featured = false }: { article: Article; featured?: boolean }) => (
    <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer ${
      featured ? 'md:col-span-2' : ''
    }`}>
      <div className={`${featured ? 'md:flex' : ''}`}>
        <div className={`${featured ? 'md:w-1/2' : ''}`}>
          <ImageWithFallback
            src={article.imageUrl}
            alt={article.title}
            className={`w-full object-cover ${featured ? 'h-48 md:h-full' : 'h-48'}`}
          />
        </div>
        <CardContent className={`p-6 ${featured ? 'md:w-1/2' : ''}`}>
          <div className="flex items-center space-x-2 mb-3">
            <Badge variant="secondary">{article.category}</Badge>
            {featured && <Badge variant="default">Featured</Badge>}
          </div>
          
          <h3 className={`font-semibold mb-2 line-clamp-2 ${featured ? 'text-xl' : 'text-lg'}`}>
            {article.title}
          </h3>
          
          <p className="text-gray-600 mb-4 line-clamp-3">
            {article.excerpt}
          </p>
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center space-x-4">
              <span>{article.author}</span>
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
          
          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-gray-500">
              {new Date(article.publishDate).toLocaleDateString()}
            </span>
            <Button variant="ghost" size="sm">
              <Share2 className="w-4 h-4 mr-1" />
              Share
            </Button>
          </div>
        </CardContent>
      </div>
    </Card>
  );

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">News & Articles</h1>
        <p className="text-gray-600">Stay updated with the latest insights and industry trends</p>
      </div>

      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="grid w-full grid-cols-6">
          {categories.map((category) => (
            <TabsTrigger key={category} value={category} className="capitalize">
              {category === 'all' ? (
                <div className="flex items-center space-x-1">
                  <Globe className="w-4 h-4" />
                  <span>All</span>
                </div>
              ) : (
                category
              )}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Featured Articles */}
      {selectedCategory === 'all' && featuredArticles.length > 0 && (
        <div className="mb-12">
          <div className="flex items-center space-x-2 mb-6">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Featured Stories</h2>
          </div>
          <div className="grid gap-6">
            {featuredArticles.map((article) => (
              <ArticleCard key={article.id} article={article} featured />
            ))}
          </div>
        </div>
      )}

      {/* Regular Articles */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-6">
          <BookOpen className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold">
            {selectedCategory === 'all' ? 'Latest Articles' : `${selectedCategory} Articles`}
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
          <Button variant="outline" size="lg">
            Load More Articles
          </Button>
        </div>
      )}
    </div>
  );
}