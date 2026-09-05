import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { diaryApi } from '../api/diary';
import { RatingDots } from '../components/common/RatingDots';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ArrowLeft, Star, Trash2, Heart } from 'lucide-react';

export const DiaryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const { data: log, isLoading } = useQuery({
    queryKey: ['diary-log', id],
    queryFn: () => diaryApi.getLogDetail(id!),
    enabled: !!id,
  });

  const handleDelete = async () => {
    if (!log) return;
    if (!window.confirm('Delete this wear log permanently?')) return;

    try {
      await diaryApi.deleteLog(log.id);
      showToast('Wear log deleted', 'info');
      navigate('/diary');
    } catch {
      showToast('Failed to delete wear log', 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 space-y-4">
        <div className="h-4 w-24 bg-surface animate-pulse rounded" />
        <div className="h-8 w-64 bg-surface animate-pulse rounded" />
        <div className="h-32 w-full bg-surface animate-pulse rounded" />
      </div>
    );
  }

  if (!log) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-3">
        <h3 className="font-serif text-xl text-text-primary">Wear log entry not found</h3>
        <Link to="/diary" className="text-xs text-accent hover:underline">
          Return to Diary
        </Link>
      </div>
    );
  }

  const isOwner = user?.username === log.username;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8 animate-fade-in">
      {/* Back button */}
      <Link
        to="/diary"
        className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Diary
      </Link>

      {/* Main Log Card */}
      <div className="vault-card p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-border/70 pb-6">
          <div className="space-y-1">
            <Link
              to={`/fragrance/${log.fragrance_id}`}
              className="text-[11px] font-label uppercase tracking-[0.2em] text-accent hover:underline font-semibold"
            >
              {log.house_name}
            </Link>
            <h1 className="font-serif text-3xl font-normal text-text-primary">
              {log.fragrance_name}
            </h1>
            <p className="font-sans text-xs text-text-secondary">
              Wear logged by @{log.username} on {log.wear_date}
            </p>
          </div>

          {log.is_favorite && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-accent/10 border border-accent/30 rounded text-accent text-xs font-label uppercase tracking-wider font-semibold self-start">
              <Star className="w-3.5 h-3.5 fill-accent" /> Standout Wear
            </div>
          )}
        </div>

        {/* Sensory Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-surface rounded">
          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Rating
            </span>
            <div className="flex items-center gap-2">
              <span className="font-serif text-xl font-semibold text-text-primary">
                {log.rating || '—'}
              </span>
              <RatingDots rating={log.rating} size="sm" />
            </div>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Occasion
            </span>
            <p className="font-sans text-sm font-medium text-text-primary">{log.occasion}</p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Sprays
            </span>
            <p className="font-sans text-sm font-medium text-text-primary">{log.sprays} sprays</p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Longevity
            </span>
            <p className="font-sans text-sm font-medium text-text-primary">
              {log.longevity_hours ? `${log.longevity_hours} hours` : '—'}
            </p>
          </div>
        </div>

        {/* Review observation text */}
        {log.review_text && (
          <div className="space-y-2 pt-2">
            <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
              Observations & Evolution
            </h3>
            <p className="font-sans text-sm text-text-primary leading-relaxed whitespace-pre-line bg-surface/30 p-4 border border-border/50 rounded">
              {log.review_text}
            </p>
          </div>
        )}

        {/* Likes / Community appreciation */}
        <div className="flex items-center gap-2 text-xs font-sans text-text-secondary pt-2">
          <Heart className="w-3.5 h-3.5 text-accent fill-accent" />
          <span>{log.like_count} curators found this impression helpful</span>
        </div>

        {/* Owner actions */}
        {isOwner && (
          <div className="pt-4 border-t border-border/60 flex justify-end gap-3">
            <Button variant="danger" size="sm" onClick={handleDelete}>
              <Trash2 className="w-3.5 h-3.5" /> Delete Entry
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
