import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { FragranceCard } from '../components/catalog/FragranceCard';
import { FragranceCardSkeleton } from '../components/common/Skeleton';
import { Button } from '../components/common/Button';
import { Pagination } from '../components/common/Pagination';
import { useAuth } from '../context/AuthContext';
import { Search, Sparkles } from 'lucide-react';

const PAGE_SIZE = 24;

export const HomePage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();

  const initialQuery = searchParams.get('q') || '';
  const initialPage = parseInt(searchParams.get('page') || '1', 10);
  const validatedInitialPage = isNaN(initialPage) || initialPage < 1 ? 1 : initialPage;

  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [activeSearch, setActiveSearch] = useState(initialQuery);
  const [page, setPage] = useState(validatedInitialPage);

  const catalogHeaderRef = useRef<HTMLDivElement>(null);

  // Keep state synchronized if URL search params change (e.g. back/forward navigation)
  useEffect(() => {
    const urlQuery = searchParams.get('q') || '';
    const urlPage = parseInt(searchParams.get('page') || '1', 10);
    const validUrlPage = isNaN(urlPage) || urlPage < 1 ? 1 : urlPage;

    if (urlQuery !== activeSearch) {
      setSearchQuery(urlQuery);
      setActiveSearch(urlQuery);
    }
    if (validUrlPage !== page) {
      setPage(validUrlPage);
    }
  }, [searchParams]);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['fragrances', activeSearch, page],
    queryFn: async () => {
      const res = await catalogApi.getFragrances({
        page,
        q: activeSearch || undefined,
      });
      return res;
    },
  });

  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);
  const fragrances = data?.results || [];

  // Prefetch next and previous pages for instant response
  useEffect(() => {
    if (page < totalPages) {
      queryClient.prefetchQuery({
        queryKey: ['fragrances', activeSearch, page + 1],
        queryFn: () =>
          catalogApi.getFragrances({
            page: page + 1,
            q: activeSearch || undefined,
          }),
      });
    }
    if (page > 1) {
      queryClient.prefetchQuery({
        queryKey: ['fragrances', activeSearch, page - 1],
        queryFn: () =>
          catalogApi.getFragrances({
            page: page - 1,
            q: activeSearch || undefined,
          }),
      });
    }
  }, [totalPages, activeSearch, page, queryClient]);

  const updateUrlParams = (newPage: number, query: string) => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (newPage > 1) params.set('page', newPage.toString());
    setSearchParams(params, { replace: false });
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    updateUrlParams(newPage, activeSearch);

    // Smooth scroll to catalog grid when changing page
    if (catalogHeaderRef.current) {
      const headerTop = catalogHeaderRef.current.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: Math.max(0, headerTop), behavior: 'smooth' });
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = searchQuery.trim();
    setActiveSearch(trimmed);
    setPage(1);
    updateUrlParams(1, trimmed);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setActiveSearch('');
    setPage(1);
    updateUrlParams(1, '');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Editorial Hero Banner */}
      <section className="text-center py-10 md:py-16 space-y-4 max-w-2xl mx-auto">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.3em] text-accent">
          {isAuthenticated ? `Curator Showcase · @${user?.username}` : 'The Olfactory Archive'}
        </span>
        <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl font-normal text-text-primary tracking-tight leading-tight">
          Savor Every Note, <br className="hidden sm:inline" />
          Capture Every Wear.
        </h1>
        <p className="font-sans text-xs sm:text-sm text-text-secondary leading-relaxed max-w-lg mx-auto">
          Explore over 24,000 catalogued fragrance compositions with community insights, olfactory pyramids, and personalized wear journals.
        </p>

        {/* Hero Search Bar */}
        <form onSubmit={handleSearchSubmit} className="pt-4 max-w-md mx-auto flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name or house (e.g. Creed, Aventus)..."
              className="form-input pl-9 text-xs"
            />
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
          </div>
          <Button type="submit" variant="accent" size="sm">
            Search
          </Button>
        </form>
      </section>

      {/* Active Search / Personalization Filter Status & Anchor */}
      <div ref={catalogHeaderRef} className="flex items-center justify-between border-b border-border/80 pb-4 text-xs scroll-mt-24">
        <div className="flex items-center gap-2">
          {activeSearch ? (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-text-secondary">Results for:</span>
              <span className="font-serif text-base font-semibold text-text-primary">
                "{activeSearch}"
              </span>
              <button
                onClick={handleClearSearch}
                className="text-[10px] font-label uppercase tracking-widest text-accent hover:underline ml-2"
              >
                Clear Search
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-accent" />
              <span className="font-label uppercase tracking-widest text-text-primary font-medium">
                {isAuthenticated ? 'Curated For Your Olfactory Profile' : 'Complete Catalogue'}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 text-text-secondary text-[11px] font-label uppercase tracking-wider">
          <span>{isLoading ? 'Loading...' : `${totalCount.toLocaleString()} Compositions`}</span>
        </div>
      </div>

      {/* Fragrance Grid with Skeletons or Empty State */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: PAGE_SIZE }).map((_, i) => (
            <FragranceCardSkeleton key={i} />
          ))}
        </div>
      ) : fragrances.length > 0 ? (
        <div className="space-y-8">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {fragrances.map((fragrance) => (
              <FragranceCard key={fragrance.id} fragrance={fragrance} />
            ))}
          </div>

          {/* Pagination Controls */}
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            onPageChange={handlePageChange}
            disabled={isFetching}
            itemLabel="Compositions"
          />
        </div>
      ) : (
        <div className="text-center py-16 space-y-3 bg-surface/50 border border-border/60 rounded">
          <p className="font-serif text-xl text-text-primary">No fragrances found</p>
          <p className="text-xs text-text-secondary">
            Try adjusting your search keywords or clear your query.
          </p>
          <Button variant="outline" size="sm" onClick={handleClearSearch}>
            Reset Catalogue
          </Button>
        </div>
      )}
    </div>
  );
};
