import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Select } from '../common/Select';
import { RatingDots } from '../common/RatingDots';
import { catalogApi } from '../../api/catalog';
import { diaryApi } from '../../api/diary';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { Search, Loader2, Sparkles, Star } from 'lucide-react';
import type { SearchResultItem, ScentLogFormValues } from '../../types';

export interface ScentLogModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialFragrance?: { id: number; name: string; house_name?: string };
  onSuccess?: () => void;
}

export const ScentLogModal: React.FC<ScentLogModalProps> = ({
  isOpen,
  onClose,
  initialFragrance,
  onSuccess,
}) => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedFragrance, setSelectedFragrance] = useState<{ id: number; name: string; house?: string } | null>(
    null
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<ScentLogFormValues>({
    defaultValues: {
      wear_date: new Date().toISOString().split('T')[0],
      rating: 4.0,
      occasion: 'Casual',
      sprays: 3,
      sillage_rating: 3,
      longevity_hours: 6,
      review_text: '',
      is_favorite: false,
    },
  });

  const ratingValue = watch('rating') || 0;
  const isFavorite = watch('is_favorite');

  useEffect(() => {
    if (initialFragrance) {
      setSelectedFragrance({
        id: initialFragrance.id,
        name: initialFragrance.name,
        house: initialFragrance.house_name,
      });
      setValue('fragrance', initialFragrance.id);
    } else {
      setSelectedFragrance(null);
    }
  }, [initialFragrance, setValue, isOpen]);

  // Debounced autocomplete search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    setIsSearching(true);
    const handler = setTimeout(async () => {
      try {
        const res = await catalogApi.search(searchQuery.trim());
        setSearchResults(res.results);
      } catch {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(handler);
  }, [searchQuery]);

  const onSubmit = async (data: ScentLogFormValues) => {
    if (!selectedFragrance) {
      showToast('Please select a fragrance first', 'error');
      return;
    }
    if (!isAuthenticated) {
      showToast('Please sign in to log your wear session', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      await diaryApi.createLog({
        ...data,
        fragrance: selectedFragrance.id,
      });
      showToast(`Logged "${selectedFragrance.name}" to your Scent Diary`, 'success');
      reset();
      setSelectedFragrance(null);
      setSearchQuery('');
      onClose();
      onSuccess?.();
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.fragrance?.[0] ||
        err.response?.data?.detail ||
        'Failed to save wear session. Ensure the fragrance is added to your wardrobe.';
      showToast(errorMsg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Log Wear Session"
      subtitle="Capture impressions, projection, and skin performance."
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Fragrance Selector */}
        <div className="space-y-1.5">
          <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
            Fragrance Selection *
          </label>

          {selectedFragrance ? (
            <div className="p-3 bg-surface border border-accent/40 rounded flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-4 h-4 text-accent shrink-0" />
                <div>
                  <p className="font-serif text-sm font-semibold text-text-primary">
                    {selectedFragrance.name}
                  </p>
                  {selectedFragrance.house && (
                    <p className="text-[11px] font-label uppercase tracking-wider text-text-secondary">
                      {selectedFragrance.house}
                    </p>
                  )}
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedFragrance(null);
                  setValue('fragrance', 0);
                }}
                className="text-xs font-label uppercase tracking-widest text-text-secondary hover:text-accent"
              >
                Change
              </button>
            </div>
          ) : (
            <div className="relative">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search catalogue to log a wear..."
                  className="form-input pl-9"
                />
                <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                {isSearching && (
                  <Loader2 className="w-4 h-4 text-accent animate-spin absolute right-3 top-1/2 -translate-y-1/2" />
                )}
              </div>

              {/* Autocomplete Dropdown */}
              {searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-white border border-border rounded shadow-lg z-20 divide-y divide-border/50">
                  {searchResults.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        setSelectedFragrance(item);
                        setValue('fragrance', item.id);
                        setSearchQuery('');
                        setSearchResults([]);
                      }}
                      className="w-full px-3 py-2 text-left hover:bg-surface flex items-center justify-between text-xs"
                    >
                      <span className="font-medium text-text-primary">{item.name}</span>
                      <span className="text-text-secondary text-[11px] uppercase tracking-wider">
                        {item.house}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Date & Occasion */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label="Wear Date *"
            type="date"
            {...register('wear_date', { required: 'Date is required' })}
            error={errors.wear_date?.message}
          />

          <Select
            label="Occasion"
            {...register('occasion')}
            options={[
              { value: 'Casual', label: 'Casual Wear' },
              { value: 'Work', label: 'Work & Office' },
              { value: 'Evening', label: 'Evening Out' },
              { value: 'Formal', label: 'Formal Gathering' },
              { value: 'Special', label: 'Special Occasion' },
            ]}
          />
        </div>

        {/* Rating & Sprays */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3 bg-surface/40 rounded-sm border border-border/50">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
                Personal Rating
              </label>
              <span className="font-serif text-sm font-semibold text-accent">
                {ratingValue ? Number(ratingValue).toFixed(1) : '0.0'} / 5.0
              </span>
            </div>
            <div className="flex items-center gap-3">
              <RatingDots
                rating={ratingValue}
                size="lg"
                interactive
                onChange={(val) => setValue('rating', val)}
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary mb-1.5">
              Sprays Applied
            </label>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setValue('sprays', Math.max(1, (watch('sprays') || 1) - 1))}
                className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-sm font-bold text-text-primary hover:border-accent active:bg-surface"
              >
                -
              </button>
              <input
                type="number"
                min="1"
                max="20"
                className="w-16 h-8 text-center bg-white border border-border rounded text-xs font-semibold text-text-primary"
                {...register('sprays', { valueAsNumber: true })}
              />
              <button
                type="button"
                onClick={() => setValue('sprays', Math.min(20, (watch('sprays') || 1) + 1))}
                className="w-8 h-8 rounded border border-border bg-white flex items-center justify-center text-sm font-bold text-text-primary hover:border-accent active:bg-surface"
              >
                +
              </button>
              <span className="text-xs text-text-secondary pl-1 font-label">sprays</span>
            </div>
          </div>
        </div>

        {/* Sillage & Longevity */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Select
            label="Projection / Sillage"
            {...register('sillage_rating', { valueAsNumber: true })}
            options={[
              { value: 1, label: '1 — Intimate / Skin Scent' },
              { value: 2, label: '2 — Soft Projection' },
              { value: 3, label: '3 — Moderate Trail' },
              { value: 4, label: '4 — Strong Presence' },
              { value: 5, label: '5 — Enormous Sillage' },
            ]}
          />

          <Input
            label="Longevity (Skin Hours)"
            type="number"
            min="1"
            max="24"
            placeholder="e.g. 8"
            {...register('longevity_hours', { valueAsNumber: true })}
          />
        </div>

        {/* Notes & Impression */}
        <div className="space-y-1.5">
          <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
            Wear Observations & Impressions
          </label>
          <textarea
            rows={3}
            placeholder="How did the opening evolve into the drydown? How did it perform on skin throughout the day?"
            className="form-input text-xs"
            {...register('review_text')}
          />
        </div>

        {/* Standout Favorite checkbox */}
        <div className="pt-1">
          <button
            type="button"
            onClick={() => setValue('is_favorite', !isFavorite)}
            className={`inline-flex items-center gap-2 px-3 py-2 rounded border transition-all text-xs font-label uppercase tracking-wider ${
              isFavorite
                ? 'bg-accent/10 border-accent text-accent font-semibold'
                : 'bg-white border-border/70 text-text-secondary hover:border-accent/40'
            }`}
          >
            <Star className={`w-3.5 h-3.5 ${isFavorite ? 'fill-accent text-accent' : 'text-text-secondary'}`} />
            <span>Mark as Standout Wear</span>
          </button>
        </div>

        {/* Actions */}
        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2.5 pt-4 border-t border-border/60">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting} className="w-full sm:w-auto">
            Cancel
          </Button>
          <Button type="submit" variant="accent" isLoading={isSubmitting} className="w-full sm:w-auto">
            Save to Diary
          </Button>
        </div>
      </form>
    </Modal>
  );
};
