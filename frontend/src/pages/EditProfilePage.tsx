import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { accountsApi } from '../api/accounts';
import { catalogApi } from '../api/catalog';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ArrowLeft, Search, Sparkles } from 'lucide-react';
import type { SearchResultItem } from '../types';

interface EditProfileFormValues {
  display_name: string;
  bio: string;
  location: string;
  avatar_url: string;
  email: string;
}

export const EditProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Signature fragrance search
  const [fragranceQuery, setFragranceQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [selectedFragrance, setSelectedFragrance] = useState<{ id: number; name: string } | null>(
    user?.favorite_fragrance || null
  );

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<EditProfileFormValues>({
    defaultValues: {
      display_name: user?.display_name || '',
      bio: user?.bio || '',
      location: user?.location || '',
      avatar_url: user?.avatar_url || '',
      email: '',
    },
  });

  useEffect(() => {
    if (user) {
      setValue('display_name', user.display_name || '');
      setValue('bio', user.bio || '');
      setValue('location', user.location || '');
      setValue('avatar_url', user.avatar_url || '');
      setSelectedFragrance(user.favorite_fragrance);
    }
  }, [user, setValue]);

  // Fragrance autocomplete
  useEffect(() => {
    if (!fragranceQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const handler = setTimeout(async () => {
      try {
        const res = await catalogApi.search(fragranceQuery.trim());
        setSearchResults(res.results);
      } catch {
        setSearchResults([]);
      }
    }, 250);
    return () => clearTimeout(handler);
  }, [fragranceQuery]);

  const onSubmit = async (data: EditProfileFormValues) => {
    setIsSubmitting(true);
    try {
      await accountsApi.updateProfile({
        ...data,
        favorite_fragrance: selectedFragrance ? selectedFragrance.id : null,
      });
      await refreshUser();
      showToast('Curator dossier updated', 'success');
      navigate(`/profile/${user?.username}`);
    } catch {
      showToast('Failed to update profile details', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-8 animate-fade-in">
      <Link
        to={`/profile/${user?.username}`}
        className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Dossier
      </Link>

      <div className="border-b border-border/80 pb-6 space-y-1">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Curator Configuration
        </span>
        <h1 className="font-serif text-3xl font-normal text-text-primary">
          Edit Profile Dossier
        </h1>
        <p className="font-sans text-xs text-text-secondary">
          Update your public curator bio, signature fragrance, and avatar.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="vault-card p-6 sm:p-8 space-y-6">
        <Input
          label="Display Name"
          placeholder="e.g. Alexander V."
          {...register('display_name')}
          error={errors.display_name?.message}
        />

        <div className="space-y-1.5">
          <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
            Olfactory Biography
          </label>
          <textarea
            rows={4}
            placeholder="Share your fragrance philosophy, favorite accords, and scent memories..."
            className="form-input"
            {...register('bio')}
          />
        </div>

        <Input
          label="Location"
          placeholder="e.g. Paris, France"
          {...register('location')}
        />

        <Input
          label="Avatar Image URL"
          placeholder="https://images.unsplash.com/..."
          {...register('avatar_url')}
          helperText="Direct URL to your curator photo or avatar image."
        />

        {/* Signature Fragrance Picker */}
        <div className="space-y-1.5 pt-2 border-t border-border/60">
          <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
            Signature Fragrance
          </label>

          {selectedFragrance ? (
            <div className="p-3 bg-surface border border-accent/40 rounded flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent" />
                <span className="font-serif text-sm font-semibold text-text-primary">
                  {selectedFragrance.name}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFragrance(null)}
                className="text-xs font-label uppercase tracking-widest text-text-secondary hover:text-accent"
              >
                Change
              </button>
            </div>
          ) : (
            <div className="relative">
              <input
                type="text"
                value={fragranceQuery}
                onChange={(e) => setFragranceQuery(e.target.value)}
                placeholder="Search catalogue to assign your signature fragrance..."
                className="form-input pl-9"
              />
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />

              {searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-white border border-border rounded shadow-lg z-20 divide-y divide-border/50">
                  {searchResults.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        setSelectedFragrance(item);
                        setFragranceQuery('');
                        setSearchResults([]);
                      }}
                      className="w-full px-3 py-2 text-left hover:bg-surface flex items-center justify-between text-xs"
                    >
                      <span className="font-medium text-text-primary">{item.name}</span>
                      <span className="text-text-secondary text-[10px] uppercase tracking-wider">
                        {item.house}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-6 border-t border-border/80">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate(`/profile/${user?.username}`)}
          >
            Cancel
          </Button>
          <Button type="submit" variant="accent" isLoading={isSubmitting}>
            Save Dossier
          </Button>
        </div>
      </form>
    </div>
  );
};
