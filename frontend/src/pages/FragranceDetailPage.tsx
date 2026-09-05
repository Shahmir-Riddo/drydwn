import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { accountsApi } from '../api/accounts';
import { OlfactoryPyramid } from '../components/catalog/OlfactoryPyramid';
import { ExperienceBars } from '../components/catalog/ExperienceBars';
import { ReviewSummary } from '../components/catalog/ReviewSummary';
import { ReviewCard } from '../components/catalog/ReviewCard';
import { ScentLogModal } from '../components/diary/ScentLogModal';
import { Button } from '../components/common/Button';
import { FragranceDetailSkeleton } from '../components/common/Skeleton';
import { OptimizedImage } from '../components/common/OptimizedImage';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Sparkles, Plus, Check, ArrowLeft, Bookmark, ChevronRight } from 'lucide-react';
import type { WardrobeShelf, CommunityInsightCategory } from '../types';

export const FragranceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [reviewSort, setReviewSort] = useState<'recent' | 'highest' | 'lowest' | 'helpful'>('recent');
  const [reviewPage, setReviewPage] = useState(1);
  const [savedShelf, setSavedShelf] = useState<string | null>(null);
  const [shelfDropdown, setShelfDropdown] = useState(false);

  // Fragrance Detail query
  const {
    data: fragrance,
    isLoading: isDetailLoading,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ['fragrance', id],
    queryFn: () => catalogApi.getFragranceDetail(id!),
    enabled: !!id,
  });

  // Reviews list query
  const {
    data: reviewsData,
    isLoading: isReviewsLoading,
    refetch: refetchReviews,
  } = useQuery({
    queryKey: ['fragrance-reviews', id, reviewSort, reviewPage],
    queryFn: () => catalogApi.getFragranceReviews(id!, { sort: reviewSort, page: reviewPage }),
    enabled: !!id,
  });

  const currentShelf = savedShelf || fragrance?.current_shelf;

  const handleShelfChange = async (shelf: WardrobeShelf) => {
    if (!fragrance) return;
    if (!isAuthenticated) {
      showToast('Please sign in to organize fragrances in your wardrobe', 'info');
      return;
    }
    try {
      await accountsApi.addToWardrobe(fragrance.id, { shelf });
      setSavedShelf(shelf);
      setShelfDropdown(false);
      showToast(`Added "${fragrance.name}" to your ${shelf} shelf`, 'success');
    } catch {
      showToast('Failed to update wardrobe shelf', 'error');
    }
  };

  const handleVoteSuccess = (newCategories: CommunityInsightCategory[], totalVoters: number) => {
    if (fragrance) {
      fragrance.community_insights = newCategories;
      fragrance.total_voters = totalVoters;
    }
    refetchDetail();
  };

  if (isDetailLoading) {
    return <FragranceDetailSkeleton />;
  }

  if (!fragrance) {
    return (
      <div className="max-w-xl mx-auto py-20 px-4 text-center space-y-4">
        <h2 className="font-serif text-2xl text-text-primary">Fragrance not found</h2>
        <p className="text-xs text-text-secondary">The requested fragrance does not exist in the vault catalogue.</p>
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-wider text-accent">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Catalogue
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-8 sm:space-y-12 animate-fade-in pb-16">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[11px] font-label uppercase tracking-widest text-text-secondary overflow-x-auto whitespace-nowrap py-1">
        <Link to="/" className="hover:text-text-primary transition-colors">
          Catalogue
        </Link>
        <ChevronRight className="w-3 h-3 text-border shrink-0" />
        <Link to={`/houses/${fragrance.house.id}`} className="hover:text-text-primary transition-colors">
          {fragrance.house.name}
        </Link>
        <ChevronRight className="w-3 h-3 text-border shrink-0" />
        <span className="text-text-primary font-medium truncate">{fragrance.name}</span>
      </nav>

      {/* Main Fragrance Showcase Hero */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 sm:gap-8 lg:gap-12 items-start">
        {/* Left: Bottle Image Presentation with Ambient Pedestal */}
        <div className="md:col-span-5 bg-gradient-to-b from-white via-[#FAF9F6] to-surface border border-border/80 rounded-xl sm:rounded-sm p-6 sm:p-8 flex items-center justify-center relative aspect-[4/3] sm:aspect-[3/4] shadow-[0_4px_24px_rgba(0,0,0,0.03)] overflow-hidden">
          {/* Ambient Glow */}
          <div className="absolute inset-0 bg-radial from-accent/[0.04] to-transparent pointer-events-none" />

          <OptimizedImage
            src={fragrance.image_url}
            alt={fragrance.name}
            priority={true}
            containerClassName="w-full h-full flex items-center justify-center"
            className="max-h-full max-w-full object-contain filter drop-shadow-[0_12px_24px_rgba(0,0,0,0.12)] transition-transform duration-500 ease-luxury hover:scale-105"
            fallback={
              <div className="text-center space-y-2 text-text-secondary/40">
                <Sparkles className="w-10 h-10 mx-auto text-accent/40" />
                <span className="font-label text-xs uppercase tracking-widest block">DRYDOWN Vault</span>
              </div>
            }
          />

          {/* Floating Badges */}
          <div className="absolute top-3.5 left-3.5 flex items-center gap-2">
            <span className="text-[9px] sm:text-[10px] font-label uppercase tracking-widest text-text-secondary bg-white/90 backdrop-blur-sm px-2 py-0.5 rounded border border-border/70 shadow-xs">
              {fragrance.gender}
            </span>
            {fragrance.release_year && (
              <span className="text-[9px] sm:text-[10px] font-label uppercase tracking-widest text-text-secondary bg-white/90 backdrop-blur-sm px-2 py-0.5 rounded border border-border/70 shadow-xs">
                {fragrance.release_year}
              </span>
            )}
          </div>
        </div>

        {/* Right: Metadata & Actions */}
        <div className="md:col-span-7 space-y-5 sm:space-y-6">
          <div className="space-y-1 sm:space-y-1.5">
            <Link
              to={`/houses/${fragrance.house.id}`}
              className="inline-block font-label text-[11px] sm:text-xs uppercase tracking-[0.25em] font-semibold text-accent hover:text-accent-hover transition-colors"
            >
              {fragrance.house.name}
            </Link>
            <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-normal text-text-primary tracking-tight leading-tight">
              {fragrance.name}
            </h1>
          </div>

          {/* Action Buttons Row */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 pt-1">
            <Button
              variant="accent"
              onClick={() => setLogModalOpen(true)}
              className="w-full sm:w-auto py-3 text-xs tracking-wider"
            >
              <Plus className="w-4 h-4 stroke-[2]" /> Log Wear Session
            </Button>

            {/* Wardrobe Shelf Dropdown */}
            <div className="relative w-full sm:w-auto">
              <Button
                variant={currentShelf ? 'outline' : 'ghost'}
                onClick={() => setShelfDropdown(!shelfDropdown)}
                className={`w-full sm:w-auto py-3 text-xs tracking-wider ${
                  currentShelf ? 'border-accent text-accent bg-accent/[0.04]' : 'border-border/80'
                }`}
              >
                {currentShelf ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>On {currentShelf} Shelf</span>
                  </>
                ) : (
                  <>
                    <Bookmark className="w-3.5 h-3.5" />
                    <span>Add to Wardrobe</span>
                  </>
                )}
              </Button>

              {shelfDropdown && (
                <>
                  <div className="fixed inset-0 z-30" onClick={() => setShelfDropdown(false)} />
                  <div className="absolute top-full left-0 right-0 sm:right-auto sm:w-44 mt-1.5 bg-white border border-border rounded shadow-xl py-1.5 z-40 animate-slide-up text-xs font-sans">
                    {(['Owned', 'Wishlist', 'Tried', 'Want to Try'] as WardrobeShelf[]).map((shelf) => (
                      <button
                        key={shelf}
                        type="button"
                        onClick={() => handleShelfChange(shelf)}
                        className="w-full px-3.5 py-2 text-left text-[11px] font-label uppercase tracking-wider hover:bg-surface flex items-center justify-between transition-colors"
                      >
                        <span>{shelf}</span>
                        {currentShelf === shelf && <Check className="w-3.5 h-3.5 text-accent" />}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Olfactory Pyramid Component */}
          <div className="pt-5 border-t border-border/80">
            <OlfactoryPyramid
              topNotes={fragrance.top_notes || []}
              heartNotes={fragrance.heart_notes || []}
              baseNotes={fragrance.base_notes || []}
            />
          </div>
        </div>
      </div>

      {/* Community Experience Bars */}
      {fragrance.community_insights && fragrance.community_insights.length > 0 && (
        <section className="pt-6 sm:pt-8 border-t border-border/80">
          <ExperienceBars
            fragranceId={fragrance.id}
            categories={fragrance.community_insights}
            totalVoters={fragrance.total_voters || 0}
            onVoteSuccess={handleVoteSuccess}
          />
        </section>
      )}

      {/* Reviews & Star Rating Section */}
      <section className="pt-6 sm:pt-8 border-t border-border/80 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-serif text-2xl font-normal text-text-primary">
              Curator Reviews & Wear Logs
            </h3>
            <p className="font-sans text-xs text-text-secondary mt-0.5">
              Reflections, sillage notes, and longevity insights from fellow collectors.
            </p>
          </div>

          <Button variant="outline" size="sm" onClick={() => setLogModalOpen(true)} className="self-start sm:self-auto">
            <Plus className="w-3.5 h-3.5" /> Write Impression
          </Button>
        </div>

        {/* Rating Breakdown Chart */}
        {fragrance.reviews_summary && (
          <ReviewSummary summary={fragrance.reviews_summary} />
        )}

        {/* Sort Filter Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border/60 pb-3 gap-2 text-xs">
          <div className="flex items-center gap-2 sm:gap-4 overflow-x-auto whitespace-nowrap py-1">
            <span className="text-[10px] sm:text-[11px] font-label uppercase tracking-widest text-text-secondary font-semibold">
              Sort:
            </span>
            {(['recent', 'highest', 'lowest', 'helpful'] as const).map((sortOpt) => (
              <button
                key={sortOpt}
                onClick={() => {
                  setReviewSort(sortOpt);
                  setReviewPage(1);
                }}
                className={`font-label text-xs uppercase tracking-wider px-2 py-0.5 rounded transition-colors ${
                  reviewSort === sortOpt
                    ? 'text-accent font-semibold bg-accent/10'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                {sortOpt}
              </button>
            ))}
          </div>

          <span className="text-[11px] font-sans text-text-secondary">
            Page {reviewsData?.page || 1} of {reviewsData?.num_pages || 1}
          </span>
        </div>

        {/* Reviews List */}
        {isReviewsLoading ? (
          <div className="py-12 text-center text-xs text-text-secondary">Loading reviews...</div>
        ) : reviewsData?.reviews && reviewsData.reviews.length > 0 ? (
          <div className="divide-y divide-border/60">
            {reviewsData.reviews.map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        ) : (
          <div className="py-12 px-4 text-center space-y-2 bg-surface/30 border border-border/60 rounded">
            <p className="font-serif text-base text-text-primary">No wear reviews logged yet</p>
            <p className="text-xs text-text-secondary max-w-sm mx-auto">
              Be the first curator to log your skin impression and projection insights for this fragrance.
            </p>
          </div>
        )}

        {/* Pagination buttons */}
        {reviewsData && reviewsData.num_pages > 1 && (
          <div className="flex justify-between items-center pt-4">
            <Button
              variant="outline"
              size="sm"
              disabled={!reviewsData.has_previous}
              onClick={() => setReviewPage((prev) => Math.max(1, prev - 1))}
            >
              ← Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!reviewsData.has_next}
              onClick={() => setReviewPage((prev) => prev + 1)}
            >
              Next →
            </Button>
          </div>
        )}
      </section>

      {/* Scent Log Modal prefilled */}
      <ScentLogModal
        isOpen={logModalOpen}
        onClose={() => setLogModalOpen(false)}
        initialFragrance={{
          id: fragrance.id,
          name: fragrance.name,
          house_name: fragrance.house.name,
        }}
        onSuccess={() => {
          refetchReviews();
          refetchDetail();
        }}
      />
    </div>
  );
};
