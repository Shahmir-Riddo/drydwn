import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { accountsApi } from '../api/accounts';
import { ShelfView } from '../components/wardrobe/ShelfView';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { Layers, Plus } from 'lucide-react';

export const WardrobePage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['wardrobe'],
    queryFn: () => accountsApi.getWardrobe(),
    enabled: isAuthenticated,
  });

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 text-center space-y-4">
        <Layers className="w-10 h-10 text-accent/60 mx-auto" />
        <h2 className="font-serif text-2xl text-text-primary">Curator Wardrobe</h2>
        <p className="font-sans text-xs text-text-secondary">
          Sign in to organize your flacons, wishlist targets, sample tests, and personal fragrance ratings.
        </p>
        <div className="pt-2 flex justify-center gap-3">
          <Link to="/login">
            <Button variant="accent">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button variant="outline">Create Vault Account</Button>
          </Link>
        </div>
      </div>
    );
  }

  const items = data?.results || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Curator Collection · @{user?.username}
          </span>
          <h1 className="font-serif text-3xl font-normal text-text-primary tracking-tight mt-1">
            Fragrance Wardrobe
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Organize your signature collection across physical flacons, wishlists, and olfactive trials.
          </p>
        </div>

        <Link to="/">
          <Button variant="outline">
            <Plus className="w-3.5 h-3.5" /> Explore Catalogue
          </Button>
        </Link>
      </div>

      {/* Main Shelves */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-8">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="aspect-[3/4] bg-surface animate-pulse rounded" />
          ))}
        </div>
      ) : (
        <ShelfView
          items={items}
          onItemRemoved={() => refetch()}
          onShelfChanged={() => refetch()}
        />
      )}
    </div>
  );
};
