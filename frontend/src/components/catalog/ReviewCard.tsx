import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Star } from 'lucide-react';
import { RatingDots } from '../common/RatingDots';
import { catalogApi } from '../../api/catalog';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import type { ReviewItem } from '../../types';

export interface ReviewCardProps {
  review: ReviewItem;
}

export const ReviewCard: React.FC<ReviewCardProps> = ({ review }) => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [liked, setLiked] = useState(review.is_liked_by_user);
  const [likeCount, setLikeCount] = useState(review.like_count);
  const [isLiking, setIsLiking] = useState(false);

  const handleLike = async () => {
    if (!isAuthenticated) {
      showToast('Please sign in to vote reviews as helpful', 'info');
      return;
    }

    setIsLiking(true);
    try {
      const res = await catalogApi.toggleReviewLike(review.id);
      setLiked(res.liked);
      setLikeCount(res.like_count);
    } catch {
      showToast('Failed to update like status', 'error');
    } finally {
      setIsLiking(false);
    }
  };

  return (
    <div className="py-5 sm:py-6 space-y-3.5 border-b border-border/60">
      {/* Reviewer Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5 sm:gap-3">
          <Link to={`/profile/${review.username}`} className="shrink-0 group">
            {review.avatar_url ? (
              <img
                src={review.avatar_url}
                alt={review.user_name}
                className="w-8 h-8 sm:w-9 sm:h-9 rounded-full object-cover border border-border group-hover:border-accent transition-colors"
              />
            ) : (
              <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-surface border border-border flex items-center justify-center font-label text-[11px] font-semibold text-text-primary group-hover:border-accent transition-colors">
                {review.initials || 'CR'}
              </div>
            )}
          </Link>

          <div>
            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <Link
                to={`/profile/${review.username}`}
                className="font-sans text-xs font-semibold text-text-primary hover:text-accent transition-colors"
              >
                {review.user_name}
              </Link>
              {review.is_author ? (
                <span className="text-[9px] font-label uppercase tracking-widest text-accent bg-accent/10 border border-accent/30 px-1.5 py-0.5 rounded font-semibold">
                  You
                </span>
              ) : (
                <span className="text-[9px] font-label text-text-secondary/70">
                  Verified Curator
                </span>
              )}
              {review.is_favorite && (
                <span className="inline-flex items-center gap-1 text-[9px] font-label uppercase tracking-wider text-accent font-semibold bg-amber-500/10 px-1.5 py-0.5 rounded">
                  <Star className="w-2.5 h-2.5 fill-accent" /> Standout
                </span>
              )}
            </div>
            <p className="font-sans text-[10px] sm:text-[11px] text-text-secondary/80 pt-0.5">
              Logged on {review.wear_date}
              {review.occasion && ` · ${review.occasion}`}
              {review.sprays && ` · ${review.sprays} Sprays`}
              {review.longevity_hours && ` · ${review.longevity_hours}h Wear`}
            </p>
          </div>
        </div>

        {/* Rating Dots */}
        {review.rating && (
          <div className="flex items-center gap-1.5 shrink-0">
            <RatingDots rating={review.rating} size="sm" />
            <span className="font-serif text-sm font-semibold text-text-primary">
              {Number(review.rating).toFixed(1)}
            </span>
          </div>
        )}
      </div>

      {/* Title & Review Text */}
      <div className="space-y-1.5 pl-0 sm:pl-12">
        {review.review_title && (
          <h4 className="font-serif text-base font-medium text-text-primary leading-snug">
            {review.review_title}
          </h4>
        )}
        {review.review_text && (
          <p className="font-sans text-xs text-text-secondary leading-relaxed whitespace-pre-line">
            {review.review_text}
          </p>
        )}

        {/* Descriptor tags */}
        {review.descriptor_tags && review.descriptor_tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-2">
            {review.descriptor_tags.map((tag) => (
              <span
                key={tag}
                className="text-[10px] font-label uppercase tracking-wider text-text-secondary bg-surface border border-border/70 px-2 py-0.5 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Helpful Like Button */}
      <div className="pl-0 sm:pl-12 pt-1 flex items-center justify-between">
        <button
          onClick={handleLike}
          disabled={isLiking}
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-label uppercase tracking-wider border transition-all ${
            liked
              ? 'border-accent/40 bg-accent/5 text-accent font-semibold'
              : 'border-border/60 text-text-secondary hover:text-text-primary hover:border-border bg-white'
          }`}
        >
          <Heart className={`w-3 h-3 ${liked ? 'fill-accent text-accent' : 'text-current'}`} />
          <span>Helpful ({likeCount})</span>
        </button>
      </div>
    </div>
  );
};
