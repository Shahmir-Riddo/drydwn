import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { RatingDots } from '../common/RatingDots';
import { OptimizedImage } from '../common/OptimizedImage';
import { Sparkles, Trash2, Edit2, Check } from 'lucide-react';
import { accountsApi } from '../../api/accounts';
import { useToast } from '../../context/ToastContext';
import type { WardrobeItem, WardrobeShelf } from '../../types';

export interface WardrobeItemCardProps {
  item: WardrobeItem;
  onRemove?: (id: number) => void;
  onShelfChange?: (id: number, newShelf: WardrobeShelf) => void;
}

export const WardrobeItemCard: React.FC<WardrobeItemCardProps> = ({
  item,
  onRemove,
  onShelfChange,
}) => {
  const { showToast } = useToast();
  const [shelfDropdown, setShelfDropdown] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleMoveShelf = async (shelf: WardrobeShelf) => {
    setIsUpdating(true);
    try {
      await accountsApi.addToWardrobe(item.fragrance_id, { shelf });
      showToast(`Moved to ${shelf} shelf`, 'success');
      setShelfDropdown(false);
      onShelfChange?.(item.id, shelf);
    } catch {
      showToast('Failed to update shelf', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    try {
      await accountsApi.removeFromWardrobe(item.id);
      showToast(`Removed from wardrobe`, 'info');
      onRemove?.(item.id);
    } catch {
      showToast('Failed to remove item', 'error');
    }
  };

  return (
    <div className="vault-card p-4 flex flex-col justify-between group relative overflow-hidden">
      <div>
        {/* Bottle Image */}
        <Link to={`/fragrance/${item.fragrance_id}`} className="block">
          <div className="w-full aspect-[3/4] bg-surface rounded flex items-center justify-center mb-3 group-hover:bg-surface/70 transition-colors overflow-hidden">
            <OptimizedImage
              src={item.has_image ? `/fragrance/${item.fragrance_id}/image/?size=thumb` : null}
              alt={item.fragrance_name}
              containerClassName="w-full h-full"
              className="max-h-[85%] max-w-[85%] object-contain transition-transform duration-500 group-hover:scale-105"
              fallback={<Sparkles className="w-6 h-6 text-accent/40" />}
            />
          </div>

          <p className="text-[10px] font-label uppercase tracking-[0.2em] text-text-secondary truncate">
            {item.house_name}
          </p>
          <h3 className="font-serif text-base font-medium text-text-primary group-hover:text-accent transition-colors line-clamp-1">
            {item.fragrance_name}
          </h3>
        </Link>

        {/* Rating and Bottle size */}
        <div className="flex items-center justify-between pt-2 text-xs">
          {item.personal_rating ? (
            <RatingDots rating={item.personal_rating} size="sm" />
          ) : (
            <span className="text-[10px] font-sans text-text-secondary/60 italic">Unrated</span>
          )}

          {item.bottle_size_ml && (
            <span className="text-[10px] font-label text-text-secondary">
              {item.bottle_size_ml} ml
            </span>
          )}
        </div>
      </div>

      {/* Actions footer */}
      <div className="mt-3 pt-2.5 border-t border-border/50 flex items-center justify-between">
        <div className="relative">
          <button
            onClick={() => setShelfDropdown(!shelfDropdown)}
            disabled={isUpdating}
            className="text-[10px] font-label uppercase tracking-wider text-text-secondary hover:text-text-primary flex items-center gap-1"
          >
            <span>{item.shelf}</span>
            <Edit2 className="w-2.5 h-2.5" />
          </button>

          {shelfDropdown && (
            <>
              <div
                className="fixed inset-0 z-30"
                onClick={() => setShelfDropdown(false)}
              />
              <div className="absolute bottom-full left-0 mb-1 w-32 bg-white border border-border rounded shadow-lg py-1 z-40 text-xs">
                {(['Owned', 'Wishlist', 'Tried', 'Want to Try'] as WardrobeShelf[]).map((shelf) => (
                  <button
                    key={shelf}
                    onClick={() => handleMoveShelf(shelf)}
                    className="w-full px-2.5 py-1 text-left text-[10px] font-label uppercase tracking-wider hover:bg-surface flex items-center justify-between"
                  >
                    {shelf}
                    {item.shelf === shelf && <Check className="w-3 h-3 text-accent" />}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <button
          onClick={handleRemove}
          className="text-text-secondary/60 hover:text-rose-600 transition-colors p-1"
          title="Remove from wardrobe"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
