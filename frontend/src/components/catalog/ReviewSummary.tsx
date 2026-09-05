import React from 'react';
import { RatingDots } from '../common/RatingDots';
import type { ReviewsSummary } from '../../types';

export interface ReviewSummaryProps {
  summary: ReviewsSummary;
}

export const ReviewSummary: React.FC<ReviewSummaryProps> = ({ summary }) => {
  return (
    <div className="vault-card p-6 flex flex-col md:flex-row items-center gap-8 justify-between">
      {/* Average rating large display */}
      <div className="flex flex-col items-center md:items-start text-center md:text-left space-y-1.5 shrink-0">
        <span className="font-serif text-5xl font-normal text-text-primary">
          {summary.avg_rating > 0 ? summary.avg_rating.toFixed(1) : '—'}
        </span>
        <RatingDots rating={summary.avg_rating} size="lg" />
        <p className="font-sans text-xs text-text-secondary pt-1">
          Based on {summary.total_ratings_count} ratings ({summary.total_reviews} wear reviews)
        </p>
      </div>

      {/* 5-Star distribution horizontal bars */}
      <div className="w-full max-w-sm space-y-2">
        {summary.star_breakdown.map((item) => (
          <div key={item.stars} className="flex items-center gap-3 text-xs font-sans">
            <span className="w-12 text-[11px] font-label text-text-secondary text-right shrink-0">
              {item.stars} Stars
            </span>
            <div className="flex-1 h-2 bg-surface rounded-full overflow-hidden border border-border/40">
              <div
                className="h-full bg-accent transition-all duration-500 ease-luxury rounded-full"
                style={{ width: `${item.percentage}%` }}
              />
            </div>
            <span className="w-10 text-[11px] font-label text-text-secondary/80 text-right shrink-0">
              {item.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
