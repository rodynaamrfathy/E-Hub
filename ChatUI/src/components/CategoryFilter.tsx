interface CategoryFilterProps {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

export function CategoryFilter({ activeCategory, onCategoryChange }: CategoryFilterProps) {
  const categories = [
    { id: 'all', label: 'All' },
    { id: 'news', label: 'News' },
    { id: 'articles', label: 'Articles' },
    { id: 'tutorials', label: 'Tutorials' },
    { id: 'events', label: 'Events' },
  ];

  return (
    <div className="flex gap-3 px-4 py-4 overflow-x-auto">
      {categories.map((category) => (
        <button
          key={category.id}
          onClick={() => onCategoryChange(category.id)}
          className={`px-4 py-2 rounded-2xl text-sm font-medium whitespace-nowrap transition-colors ${
            activeCategory === category.id
              ? 'bg-[#01A669] text-white font-semibold'
              : 'bg-[#f6f5f8] text-[#8e8e8e] hover:bg-gray-200'
          }`}
        >
          {category.label}
        </button>
      ))}
    </div>
  );
}