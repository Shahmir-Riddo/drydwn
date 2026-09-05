import React, { useState } from 'react';
import { WardrobeItemCard } from './WardrobeItemCard';
import { Layers, Sparkles } from 'lucide-react';
import type { WardrobeItem, WardrobeShelf } from '../../types';

export interface ShelfViewProps {
  items: WardrobeItem[];
  onItemRemoved?: (id: number) => void;
  onShelfChanged?: (id: number, newShelf: WardrobeShelf) => void;
}

export const ShelfView: React.FC<ShelfViewProps> = ({
  items,
  onItemRemoved,
  onShelfChanged,
}) => {
  const [activeShelf, setActiveShelf] = useState<WardrobeShelf | 'All'>('All');

  const shelves: Array<{ key: WardrobeShelf | 'All'; label: string }> = [
    { key: 'All', label: 'All Bottles' },
    { key: 'Owned', label: 'Owned' },
    { key: 'Wishlist', label: 'Wishlist' },
    { key: 'Tried', label: 'Tried' },
    { key: 'Want to Try', label: 'Want to Try' },
  ];

  const filteredItems =
    activeShelf === 'All' ? items : items.filter((item) => item.shelf === activeShelf);

  return (
    <div className="space-y-6">
      {/* Shelf Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-border/70 overflow-x-auto pb-px">
        {shelves.map((shelf) => {
          const count =
            shelf.key === 'All'
              ? items.length
              : items.filter((i) => i.shelf === shelf.key).length;

          const isActive = activeShelf === shelf.key;

          return (
            <button
              key={shelf.key}
              onClick={() => setActiveShelf(shelf.key)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-label uppercase tracking-widest transition-all relative shrink-0 ${
                isActive
                  ? 'text-text-primary font-semibold after:absolute after:bottom-0 after:left-0 after:w-full after:h-[2px] after:bg-accent'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <span>{shelf.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                  isActive ? 'bg-accent/10 text-accent' : 'bg-surface text-text-secondary'
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* 3D Shelf Decorative header for Owned shelf */}
      {activeShelf === 'Owned' && (
        <div className="p-4 bg-surface border-b-4 border-accent/40 rounded-t flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-accent" />
            <span className="font-serif text-base text-text-primary">Curator's Primary Collection</span>
          </div>
          <span className="font-label text-[11px] uppercase tracking-wider text-text-secondary">
            {filteredItems.length} flacons in inventory
          </span>
        </div>
      )}

      {/* Grid of bottles */}
      {filteredItems.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredItems.map((item) => (
            <WardrobeItemCard
              key={item.id}
              item={item}
              onRemove={onItemRemoved}
              onShelfChange={onShelfChanged}
            />
          ))}
        </div>
      ) : (
        <div className="py-16 text-center space-y-3 bg-surface/40 border border-border/60 rounded-sm">
          <Sparkles className="w-8 h-8 text-accent/40 mx-auto" />
          <h4 className="font-serif text-lg text-text-primary">No fragrances on this shelf</h4>
          <p className="font-sans text-xs text-text-secondary max-w-sm mx-auto">
            Browse the catalogue to discover new compositions and organize them into your personal wardrobe.
          </p>
        </div>
      )}
    </div>
  );
};
