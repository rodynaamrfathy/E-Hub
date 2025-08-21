import { useState } from 'react';
import { Search, Filter, Star, Heart, ShoppingCart, Leaf, Award, Truck } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviews: number;
  category: string;
  brand: string;
  imageUrl: string;
  ecoScore: number;
  certifications: string[];
  carbonSaved: string;
  featured: boolean;
}

export function EcoMarketplace() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const products: Product[] = [
    {
      id: '1',
      name: 'Bamboo Fiber Water Bottle',
      description: 'Sustainable water bottle made from bamboo fiber. BPA-free, dishwasher safe, and naturally antimicrobial.',
      price: 24.99,
      originalPrice: 34.99,
      rating: 4.8,
      reviews: 156,
      category: 'Home & Kitchen',
      brand: 'EcoWave',
      imageUrl: 'https://images.unsplash.com/photo-1605274280925-9dd1baacb97b?w=400',
      ecoScore: 95,
      certifications: ['Organic', 'Biodegradable'],
      carbonSaved: '2.5 kg CO2',
      featured: true,
    },
    {
      id: '2',
      name: 'Solar Power Bank 20000mAh',
      description: 'Portable solar charger with high-efficiency panels. Perfect for outdoor adventures and emergency backup.',
      price: 89.99,
      rating: 4.6,
      reviews: 89,
      category: 'Electronics',
      brand: 'SolarTech',
      imageUrl: 'https://images.unsplash.com/photo-1655300256486-4ec7251bf84e?w=400',
      ecoScore: 88,
      certifications: ['Energy Star', 'RoHS'],
      carbonSaved: '15 kg CO2',
      featured: false,
    },
    {
      id: '3',
      name: 'Organic Cotton Tote Bag Set',
      description: 'Set of 3 reusable shopping bags made from 100% organic cotton. Machine washable and ultra-durable.',
      price: 19.99,
      originalPrice: 29.99,
      rating: 4.9,
      reviews: 234,
      category: 'Bags & Accessories',
      brand: 'GreenLiving',
      imageUrl: 'https://images.unsplash.com/photo-1695548487486-3649bfc8dd9a?w=400',
      ecoScore: 92,
      certifications: ['GOTS', 'Fair Trade'],
      carbonSaved: '1.2 kg CO2',
      featured: true,
    },
    {
      id: '4',
      name: 'Bamboo Toothbrush 4-Pack',
      description: 'Biodegradable bamboo toothbrushes with soft bristles. Compostable handle and recyclable packaging.',
      price: 12.99,
      rating: 4.7,
      reviews: 312,
      category: 'Personal Care',
      brand: 'BambooBrush',
      imageUrl: 'https://images.unsplash.com/photo-1589365252845-092198ba5334?w=400',
      ecoScore: 96,
      certifications: ['Biodegradable', 'Vegan'],
      carbonSaved: '0.8 kg CO2',
      featured: false,
    },
    {
      id: '5',
      name: 'LED Smart Bulbs 6-Pack',
      description: 'Energy-efficient smart LED bulbs with 25-year lifespan. Control via app with dimming and color options.',
      price: 45.99,
      originalPrice: 65.99,
      rating: 4.5,
      reviews: 127,
      category: 'Home & Kitchen',
      brand: 'SmartGreen',
      imageUrl: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400',
      ecoScore: 85,
      certifications: ['Energy Star', 'RoHS'],
      carbonSaved: '120 kg CO2',
      featured: false,
    },
    {
      id: '6',
      name: 'Compostable Phone Case',
      description: 'Plant-based phone case that decomposes naturally. Drop protection with a conscience.',
      price: 32.99,
      rating: 4.4,
      reviews: 78,
      category: 'Electronics',
      brand: 'PlanetCase',
      imageUrl: 'https://images.unsplash.com/photo-1608043176183-4b86c41c7fea?w=400',
      ecoScore: 90,
      certifications: ['Compostable', 'Plant-Based'],
      carbonSaved: '0.5 kg CO2',
      featured: false,
    },
  ];

  const categories = ['all', 'Home & Kitchen', 'Electronics', 'Personal Care', 'Bags & Accessories'];

  const filteredProducts = products.filter(product => {
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const featuredProducts = filteredProducts.filter(product => product.featured);
  const regularProducts = filteredProducts.filter(product => !product.featured);

  const ProductCard = ({ product, featured = false }: { product: Product; featured?: boolean }) => (
    <Card className={`group overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer ${
      featured ? 'ring-2 ring-green-200' : ''
    }`}>
      <div className="relative">
        <ImageWithFallback
          src={product.imageUrl}
          alt={product.name}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-3 left-3 flex gap-2">
          {featured && <Badge className="bg-green-500">Featured</Badge>}
          <Badge variant="secondary" className="bg-white/90">
            <Leaf className="w-3 h-3 mr-1 text-green-600" />
            {product.ecoScore}
          </Badge>
        </div>
        <Button
          variant="secondary"
          size="sm"
          className="absolute top-3 right-3 w-8 h-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Heart className="w-4 h-4" />
        </Button>
        {product.originalPrice && (
          <Badge className="absolute bottom-3 left-3 bg-red-500">
            Save ${(product.originalPrice - product.price).toFixed(2)}
          </Badge>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold line-clamp-2 flex-1">{product.name}</h3>
        </div>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
        
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex items-center">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm ml-1">{product.rating}</span>
          </div>
          <span className="text-xs text-gray-500">({product.reviews} reviews)</span>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {product.certifications.slice(0, 2).map((cert) => (
            <Badge key={cert} variant="outline" className="text-xs">
              <Award className="w-3 h-3 mr-1" />
              {cert}
            </Badge>
          ))}
        </div>

        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold text-green-600">${product.price}</span>
              {product.originalPrice && (
                <span className="text-sm text-gray-500 line-through">${product.originalPrice}</span>
              )}
            </div>
            <p className="text-xs text-green-600">Saves {product.carbonSaved}</p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button className="flex-1 bg-green-600 hover:bg-green-700">
            <ShoppingCart className="w-4 h-4 mr-2" />
            Add to Cart
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Eco Marketplace</h1>
        <p className="text-gray-600">Discover sustainable products that make a difference</p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search eco-friendly products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Filter className="w-4 h-4" />
          <span>Filters</span>
        </Button>
      </div>

      {/* Categories */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="grid w-full grid-cols-5">
          {categories.map((category) => (
            <TabsTrigger key={category} value={category} className="capitalize">
              {category === 'all' ? 'All Products' : category}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Featured Products */}
      {selectedCategory === 'all' && featuredProducts.length > 0 && (
        <div className="mb-12">
          <div className="flex items-center space-x-2 mb-6">
            <Leaf className="w-5 h-5 text-green-600" />
            <h2 className="text-xl font-semibold">Featured Eco Products</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} featured />
            ))}
          </div>
        </div>
      )}

      {/* Regular Products */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">
            {selectedCategory === 'all' ? 'All Products' : selectedCategory}
          </h2>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Truck className="w-4 h-4" />
            <span>Free shipping on orders over $50</span>
          </div>
        </div>
        
        {regularProducts.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {regularProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-500 mb-2">No products found</h3>
            <p className="text-gray-400">Try adjusting your search or filters</p>
          </div>
        )}
      </div>

      {/* Load More */}
      {regularProducts.length > 0 && (
        <div className="text-center">
          <Button variant="outline" size="lg">
            Load More Products
          </Button>
        </div>
      )}
    </div>
  );
}