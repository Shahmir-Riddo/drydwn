import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Plus, Check } from 'lucide-react';
import { OptimizedImage } from '../common/OptimizedImage';
import { accountsApi } from '../../api/accounts';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import type { FragranceItem, WardrobeShelf } from '../../types';

export interface FragranceCardProps {
  fragrance: FragranceItem;
}

export const FragranceCard: React.FC<FragranceCardProps> = ({ fragrance }) => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [shelfMenuOpen, setShelfMenuOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [savedShelf, setSavedShelf] = useState<string | null>(null);

  const handleAddToShelf = async (shelf: WardrobeShelf, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      showToast('Please sign in to organize fragrances in your wardrobe', 'info');
      return;
    }

    setIsAdding(true);
    try {
      await accountsApi.addToWardrobe(fragrance.id, { shelf });
      setSavedShelf(shelf);
      setShelfMenuOpen(false);
      showToast(`Added "${fragrance.name}" to your ${shelf} shelf`, 'success');
    } catch {
      showToast('Failed to add to wardrobe', 'error');
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="group vault-card flex flex-col justify-between overflow-hidden relative">
      <Link to={`/fragrance/${fragrance.id}`} className="block p-4 flex-1">
        {/* Bottle Image Container */}
        <div className="w-full aspect-[3/4] bg-surface rounded-sm flex items-center justify-center relative overflow-hidden mb-3.5 group-hover:bg-surface/60 transition-colors">
          <OptimizedImage
            src={fragrance.thumbnail_url || fragrance.image_url}
            alt={fragrance.name}
            containerClassName="w-full h-full"
            className="max-h-[85%] max-w-[85%] object-contain transition-transform duration-500 ease-luxury group-hover:scale-105"
            fallback={
              <div className="flex flex-col items-center justify-center text-text-secondary/40">
                <Sparkles className="w-6 h-6 mb-1 text-accent/40" />
                <span className="text-[10px] font-label uppercase tracking-widest">DRYDOWN</span>
              </div>
            }
          />

          {/* Gender Badge */}
          <span className="absolute top-2.5 left-2.5 text-[9px] font-label uppercase tracking-wider text-text-secondary bg-white/90 backdrop-blur-xs border border-border/80 px-1.5 py-0.5 rounded">
            {fragrance.gender}
          </span>
        </div>

        {/* Fragrance Metadata */}
        <div className="space-y-1">
          <p className="text-[10px] font-label uppercase tracking-[0.2em] text-text-secondary truncate">
            {fragrance.house.name}
          </p>
          <h3 className="font-serif text-base font-medium text-text-primary group-hover:text-accent transition-colors duration-200 line-clamp-1">
            {fragrance.name}
          </h3>
          {fragrance.release_year && (
            <p className="text-[11px] font-sans text-text-secondary/70">
              {fragrance.release_year}
            </p>
          )}
        </div>
      </Link>

      {/* Quick Wardrobe Action bar */}
      <div className="px-4 pb-3.5 pt-1 border-t border-border/40 flex items-center justify-between">
        <div className="relative">
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              setShelfMenuOpen(!shelfMenuOpen);
            }}
            disabled={isAdding}
            className="inline-flex items-center gap-1 text-[10px] font-label uppercase tracking-wider text-text-secondary hover:text-accent transition-colors"
          >
            {savedShelf ? (
              <>
                <Check className="w-3 h-3 text-accent" />
                <span>{savedShelf}</span>
              </>
            ) : (
              <>
                <Plus className="w-3 h-3" />
                <span>Add to Shelf</span>
              </>
            )}
          </button>

          {/* Shelf options popover */}
          {shelfMenuOpen && (
            <>
              <div
                className="fixed inset-0 z-30"
                onClick={(e) => {
                  e.stopPropagation();
                  setShelfMenuOpen(false);
                }}
              />
              <div className="absolute bottom-full left-0 mb-1.5 w-36 bg-white border border-border rounded shadow-lg py-1 z-40 animate-slide-up text-xs font-sans">
                {(['Owned', 'Wishlist', 'Tried', 'Want to Try'] as WardrobeShelf[]).map((shelf) => (
                  <button
                    key={shelf}
                    onClick={(e) => handleAddToShelf(shelf, e)}
                    className="w-full px-3 py-1.5 text-left text-text-secondary hover:text-text-primary hover:bg-surface text-[11px] font-label uppercase tracking-wider flex items-center justify-between"
                  >
                    {shelf}
                    {savedShelf === shelf && <Check className="w-3 h-3 text-accent" />}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <Link
          to={`/fragrance/${fragrance.id}`}
          className="text-[10px] font-label uppercase tracking-wider text-text-secondary/70 hover:text-text-primary transition-colors"
        >
          View →
        </Link>
      </div>
    </div>
  );
};
