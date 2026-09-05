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
    <div className="py-6 space-y-3.5 border-b border-border/60">
      {/* Reviewer Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link to={`/profile/${review.username}`} className="shrink-0 group">
            {review.avatar_url ? (
              <img
                src={review.avatar_url}
                alt={review.user_name}
                className="w-9 h-9 rounded-full object-cover border border-sand group-hover:border-brass transition-colors"
              />
            ) : (
              <div className="w-9 h-9 rounded-full bg-linen border border-sand flex items-center justify-center font-label text-xs font-semibold text-tuxedo group-hover:border-brass transition-colors">
                {review.initials}
              </div>
            )}
          </Link>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <Link
                to={`/profile/${review.username}`}
                className="font-sans text-xs font-semibold text-tuxedo hover:text-brass transition-colors"
              >
                {review.user_name}
              </Link>
              {review.is_author ? (
                <span className="text-[9px] font-label uppercase tracking-widest text-brass bg-brass/10 border border-brass/30 px-1.5 py-0.5 rounded font-semibold">
                  Your Review
                </span>
              ) : (
                <span className="text-[9px] font-label text-tobacco/70 border-b border-sand/40">
                  Verified Wear
                </span>
              )}
              {review.is_favorite && (
                <span className="inline-flex items-center gap-1 text-[9px] font-label uppercase tracking-wider text-accent">
                  <Star className="w-3 h-3 fill-accent" /> Standout Wear
                </span>
              )}
            </div>
            <p className="font-sans text-[11px] text-tobacco/60">
              Logged on {review.wear_date}
              {review.occasion && ` · ${review.occasion}`}
              {review.sprays && ` · ${review.sprays} Sprays`}
              {review.longevity_hours && ` · ${review.longevity_hours}h Wear`}
            </p>
          </div>
        </div>

        {/* Rating Dots */}
        {review.rating && (
          <div className="flex items-center gap-2">
            <RatingDots rating={review.rating} size="sm" />
            <span className="font-serif text-sm font-semibold text-text-primary">
              {review.rating}
            </span>
          </div>
        )}
      </div>

      {/* Title & Review Text */}
      <div className="space-y-1 pl-12">
        {review.review_title && (
          <h4 className="font-serif text-base font-medium text-text-primary">
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
                className="text-[10px] font-label uppercase tracking-wider text-text-secondary/80 bg-surface border border-border/70 px-2 py-0.5 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Helpful Like Button */}
      <div className="pl-12 pt-1 flex items-center justify-between">
        <button
          onClick={handleLike}
          disabled={isLiking}
          className={`inline-flex items-center gap-1.5 text-[11px] font-label uppercase tracking-wider transition-colors ${
            liked ? 'text-accent font-semibold' : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <Heart className={`w-3.5 h-3.5 ${liked ? 'fill-accent text-accent' : 'text-current'}`} />
          <span>Helpful ({likeCount})</span>
        </button>
      </div>
    </div>
  );
};
