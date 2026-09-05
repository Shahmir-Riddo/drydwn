import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader2, X, Sparkles } from 'lucide-react';
import { catalogApi } from '../../api/catalog';
import { OptimizedImage } from './OptimizedImage';
import type { SearchResultItem } from '../../types';

export interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SearchModal: React.FC<SearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    const handler = setTimeout(async () => {
      try {
        const res = await catalogApi.search(query.trim());
        setResults(res.results);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setIsLoading(false);
      }
    }, 250);

    return () => clearTimeout(handler);
  }, [query]);

  if (!isOpen) return null;

  const handleSelect = (item: SearchResultItem) => {
    onClose();
    navigate(`/fragrance/${item.id}`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-espresso/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative w-full max-w-xl bg-white border border-border rounded-sm shadow-2xl z-10 overflow-hidden animate-slide-up">
        {/* Search input bar */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-border/70">
          <Search className="w-4 h-4 text-text-secondary shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search fragrances, perfume houses, or notes..."
            className="w-full bg-transparent font-sans text-sm text-text-primary placeholder:text-text-secondary/60 focus:outline-none"
          />
          {isLoading ? (
            <Loader2 className="w-4 h-4 text-accent animate-spin shrink-0" />
          ) : query ? (
            <button
              onClick={() => setQuery('')}
              className="text-text-secondary hover:text-text-primary p-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          ) : (
            <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary/60 border border-border px-1.5 py-0.5 rounded">
              ESC
            </span>
          )}
        </div>

        {/* Results / Empty state */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-border/40">
          {query.trim() && !isLoading && results.length === 0 && (
            <div className="py-8 text-center space-y-1 text-text-secondary">
              <p className="font-serif text-base text-text-primary">No fragrances found</p>
              <p className="text-xs">Try searching for a house name like "Creed" or "Diptyque"</p>
            </div>
          )}

          {!query.trim() && (
            <div className="py-6 px-4 space-y-2">
              <p className="text-[10px] font-label uppercase tracking-widest text-text-secondary font-semibold">
                Popular Searches
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                {['Aventus', 'Baccarat Rouge 540', 'Santal 33', 'Philosykos', 'Tobacco Vanille'].map(
                  (sample) => (
                    <button
                      key={sample}
                      onClick={() => setQuery(sample)}
                      className="px-2.5 py-1 text-xs bg-surface border border-border/80 rounded-sm text-text-secondary hover:text-text-primary hover:border-accent transition-colors"
                    >
                      {sample}
                    </button>
                  )
                )}
              </div>
            </div>
          )}

          {results.map((item) => (
            <button
              key={item.id}
              onClick={() => handleSelect(item)}
              className="w-full px-3 py-2.5 flex items-center gap-3 text-left hover:bg-surface/70 rounded-sm transition-colors group"
            >
              <div className="w-9 h-11 bg-surface border border-border/60 rounded flex items-center justify-center shrink-0 overflow-hidden">
                <OptimizedImage
                  src={item.thumbnail_url || item.image_url}
                  alt={item.name}
                  containerClassName="w-full h-full"
                  className="w-full h-full object-contain p-1"
                  fallback={<Sparkles className="w-3.5 h-3.5 text-accent/60" />}
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-label uppercase tracking-wider text-text-secondary group-hover:text-accent transition-colors truncate">
                  {item.house}
                </p>
                <p className="font-serif text-sm font-medium text-text-primary truncate">
                  {item.name}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
