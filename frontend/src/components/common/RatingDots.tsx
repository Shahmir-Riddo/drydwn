import React from 'react';
import { clsx } from 'clsx';

export interface RatingDotsProps {
  rating: number | string | null | undefined;
  max?: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onChange?: (rating: number) => void;
}

export const RatingDots: React.FC<RatingDotsProps> = ({
  rating,
  max = 5,
  className,
  size = 'md',
  interactive = false,
  onChange,
}) => {
  const numericRating = typeof rating === 'number' ? rating : rating ? parseFloat(rating) : 0;
  const [hoverRating, setHoverRating] = React.useState<number | null>(null);

  const currentVal = hoverRating !== null ? hoverRating : numericRating;

  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  };

  return (
    <div
      className={clsx('inline-flex items-center gap-1.5', className)}
      onMouseLeave={() => interactive && setHoverRating(null)}
    >
      {Array.from({ length: max }).map((_, i) => {
        const val = i + 1;
        const isFilled = currentVal >= val;
        const isHalf = !isFilled && currentVal >= val - 0.5;

        return (
          <button
            key={i}
            type="button"
            disabled={!interactive}
            onClick={() => interactive && onChange?.(val)}
            onMouseEnter={() => interactive && setHoverRating(val)}
            className={clsx(
              'rounded-full transition-transform',
              interactive ? 'cursor-pointer hover:scale-125 focus:outline-none' : 'cursor-default'
            )}
            title={`${val} of ${max}`}
          >
            <div
              className={clsx(
                sizeClasses[size],
                'rounded-full transition-colors',
                isFilled
                  ? 'bg-accent'
                  : isHalf
                  ? 'bg-accent/50 border border-accent'
                  : 'bg-transparent border border-border'
              )}
            />
          </button>
        );
      })}
    </div>
  );
};
