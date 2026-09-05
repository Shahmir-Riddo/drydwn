import React from 'react';
import { Link } from 'react-router-dom';
import { RatingDots } from '../common/RatingDots';
import { Star, Trash2, Edit3 } from 'lucide-react';
import type { ScentLog } from '../../types';

export interface ScentLogCardProps {
  log: ScentLog;
  onDelete?: (id: number) => void;
  onEdit?: (log: ScentLog) => void;
  showActions?: boolean;
}

export const ScentLogCard: React.FC<ScentLogCardProps> = ({
  log,
  onDelete,
  onEdit,
  showActions = true,
}) => {
  return (
    <div className="vault-card p-5 space-y-3.5 group hover:border-accent/40 transition-all">
      {/* Top row: Fragrance, House, and Date */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-0.5">
          <Link
            to={`/fragrance/${log.fragrance_id}`}
            className="text-[10px] font-label uppercase tracking-[0.2em] text-text-secondary hover:text-accent transition-colors"
          >
            {log.house_name}
          </Link>
          <Link
            to={`/diary/${log.id}`}
            className="block font-serif text-lg font-medium text-text-primary group-hover:text-accent transition-colors"
          >
            {log.fragrance_name}
          </Link>
        </div>

        <div className="text-right space-y-1">
          <span className="text-[11px] font-sans text-text-secondary">{log.wear_date}</span>
          {log.is_favorite && (
            <div className="flex items-center justify-end gap-1 text-[10px] font-label uppercase tracking-wider text-accent font-semibold">
              <Star className="w-3 h-3 fill-accent" /> Standout
            </div>
          )}
        </div>
      </div>

      {/* Badges / Rating / Stats */}
      <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-border/40 text-xs">
        {log.rating && (
          <div className="flex items-center gap-1.5 bg-surface px-2.5 py-1 rounded">
            <RatingDots rating={log.rating} size="sm" />
            <span className="font-semibold text-text-primary">{log.rating}</span>
          </div>
        )}

        <span className="text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface px-2.5 py-1 rounded">
          {log.occasion}
        </span>

        {log.sprays && (
          <span className="text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface px-2.5 py-1 rounded">
            {log.sprays} Sprays
          </span>
        )}

        {log.longevity_hours && (
          <span className="text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface px-2.5 py-1 rounded">
            {log.longevity_hours}h Skin
          </span>
        )}
      </div>

      {/* Review text if available */}
      {log.review_text && (
        <p className="font-sans text-xs text-text-secondary/90 leading-relaxed line-clamp-2 pt-1">
          {log.review_text}
        </p>
      )}

      {/* Action Footer */}
      {showActions && (
        <div className="pt-2 flex items-center justify-between border-t border-border/40 text-xs">
          <Link
            to={`/diary/${log.id}`}
            className="text-[11px] font-label uppercase tracking-wider text-text-secondary hover:text-text-primary transition-colors"
          >
            View Entry →
          </Link>

          <div className="flex items-center gap-2">
            {onEdit && (
              <button
                onClick={() => onEdit(log)}
                className="p-1 text-text-secondary hover:text-accent transition-colors"
                title="Edit Entry"
              >
                <Edit3 className="w-3.5 h-3.5" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(log.id)}
                className="p-1 text-text-secondary hover:text-rose-600 transition-colors"
                title="Delete Entry"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
