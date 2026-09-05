import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { OptimizedImage } from '../components/common/OptimizedImage';

export const HouseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: house, isLoading } = useQuery({
    queryKey: ['house', id],
    queryFn: () => catalogApi.getHouseDetail(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <div className="h-6 w-32 bg-surface animate-pulse rounded" />
        <div className="h-10 w-64 bg-surface animate-pulse rounded" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="aspect-[3/4] bg-surface animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (!house) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-3">
        <h3 className="font-serif text-xl text-text-primary">House not found</h3>
        <Link to="/houses" className="text-xs text-accent hover:underline">
          Return to House Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <Link
        to="/houses"
        className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Houses
      </Link>

      <div className="border-b border-border/80 pb-6 space-y-2">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Perfume House Atelier
        </span>
        <h1 className="font-serif text-4xl font-normal text-text-primary">{house.name}</h1>
        <p className="font-sans text-xs text-text-secondary">
          Browse all catalogued compositions crafted under the {house.name} house portfolio.
        </p>
      </div>

      {/* Fragrances list */}
      <div className="space-y-4">
        <h3 className="text-xs font-label uppercase tracking-[0.2em] text-text-secondary font-semibold">
          House Creations ({house.fragrances?.length || 0})
        </h3>

        {house.fragrances && house.fragrances.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {house.fragrances.map((f) => (
              <Link
                key={f.id}
                to={`/fragrance/${f.id}`}
                className="vault-card p-3.5 block group hover:border-accent/60 transition-all"
              >
                <div className="w-full aspect-[3/4] bg-surface rounded flex items-center justify-center mb-2.5 overflow-hidden">
                  <OptimizedImage
                    src={f.thumbnail_url || f.image_url}
                    alt={f.name}
                    containerClassName="w-full h-full"
                    className="max-h-[85%] max-w-[85%] object-contain transition-transform group-hover:scale-105"
                    fallback={<Sparkles className="w-5 h-5 text-accent/40" />}
                  />
                </div>
                <h4 className="font-serif text-sm text-text-primary group-hover:text-accent transition-colors line-clamp-1">
                  {f.name}
                </h4>
                <p className="text-[10px] font-sans text-text-secondary">
                  {f.gender} {f.release_year ? `· ${f.release_year}` : ''}
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-text-secondary bg-surface/30 rounded border border-border/60">
            No fragrances currently catalogued for this house.
          </div>
        )}
      </div>
    </div>
  );
};
