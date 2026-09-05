import React from 'react';
import { Link } from 'react-router-dom';
import { RatingDots } from '../common/RatingDots';
import { Star, Trash2, Edit3, ChevronRight, Droplets, Clock } from 'lucide-react';
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
  // Format date nicely (e.g. SEP 05, 2026 or 2026-09-05)
  const formattedDate = log.wear_date;

  return (
    <div className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-4 sm:p-5 space-y-3.5 group hover:border-accent/50 transition-all duration-300 shadow-[0_2px_12px_rgba(0,0,0,0.02)] hover:shadow-[0_4px_20px_rgba(0,0,0,0.04)]">
      {/* Top Header Row: House, Date, Standout Badge */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <Link
            to={`/fragrance/${log.fragrance_id}`}
            className="text-[10px] sm:text-[11px] font-label uppercase tracking-[0.2em] font-semibold text-accent hover:text-accent-hover transition-colors"
          >
            {log.house_name}
          </Link>
          <Link
            to={`/diary/${log.id}`}
            className="block font-serif text-lg sm:text-xl font-medium text-text-primary group-hover:text-accent transition-colors leading-snug"
          >
            {log.fragrance_name}
          </Link>
        </div>

        <div className="text-right shrink-0 space-y-1">
          <span className="inline-block text-[10px] sm:text-[11px] font-label uppercase tracking-widest text-text-secondary/70 bg-surface px-2 py-0.5 rounded border border-border/60">
            {formattedDate}
          </span>
          {log.is_favorite && (
            <div className="flex items-center justify-end gap-1 text-[9px] sm:text-[10px] font-label uppercase tracking-wider text-amber-700 font-semibold bg-amber-500/10 px-1.5 py-0.5 rounded">
              <Star className="w-2.5 h-2.5 fill-amber-600 text-amber-600" /> Standout
            </div>
          )}
        </div>
      </div>

      {/* Sensory Chips & Rating Row */}
      <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 pt-0.5 text-xs">
        {log.rating && (
          <div className="flex items-center gap-1.5 bg-surface/70 border border-border/60 px-2.5 py-1 rounded text-[11px]">
            <RatingDots rating={log.rating} size="sm" />
            <span className="font-serif font-semibold text-text-primary">{Number(log.rating).toFixed(1)}</span>
          </div>
        )}

        {log.occasion && (
          <span className="text-[10px] sm:text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface/70 border border-border/60 px-2.5 py-1 rounded">
            {log.occasion}
          </span>
        )}

        {log.sprays && (
          <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface/70 border border-border/60 px-2.5 py-1 rounded">
            <Droplets className="w-3 h-3 text-accent/70" />
            {log.sprays} Sprays
          </span>
        )}

        {log.longevity_hours && (
          <span className="inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-label uppercase tracking-wider text-text-secondary bg-surface/70 border border-border/60 px-2.5 py-1 rounded">
            <Clock className="w-3 h-3 text-accent/70" />
            {log.longevity_hours}h Skin
          </span>
        )}
      </div>

      {/* Review Observation snippet */}
      {log.review_text && (
        <p className="font-sans text-xs text-text-secondary leading-relaxed line-clamp-2 pt-0.5 italic border-l-2 border-accent/30 pl-2.5">
          "{log.review_text}"
        </p>
      )}

      {/* Action Footer */}
      {showActions && (
        <div className="pt-2 flex items-center justify-between border-t border-border/50 text-xs">
          <Link
            to={`/diary/${log.id}`}
            className="inline-flex items-center gap-1 text-[11px] font-label uppercase tracking-wider text-text-secondary hover:text-accent transition-colors font-medium"
          >
            <span>Dossier Entry</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>

          <div className="flex items-center gap-1">
            {onEdit && (
              <button
                onClick={() => onEdit(log)}
                className="p-1.5 rounded text-text-secondary hover:text-accent hover:bg-surface transition-colors"
                title="Edit Entry"
                aria-label="Edit Entry"
              >
                <Edit3 className="w-3.5 h-3.5" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(log.id)}
                className="p-1.5 rounded text-text-secondary hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Delete Entry"
                aria-label="Delete Entry"
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
