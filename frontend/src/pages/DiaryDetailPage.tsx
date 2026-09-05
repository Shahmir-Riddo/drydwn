import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { diaryApi } from '../api/diary';
import { RatingDots } from '../components/common/RatingDots';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ArrowLeft, Star, Trash2, Heart, Droplets, Clock, Sparkles } from 'lucide-react';

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
    if (!window.confirm('Delete this wear log permanently from your diary?')) return;

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
      <div className="max-w-3xl mx-auto py-12 px-4 space-y-4">
        <div className="h-4 w-24 bg-surface animate-pulse rounded" />
        <div className="h-8 w-64 bg-surface animate-pulse rounded" />
        <div className="h-40 w-full bg-surface animate-pulse rounded" />
      </div>
    );
  }

  if (!log) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 text-center space-y-3">
        <h3 className="font-serif text-xl text-text-primary">Wear log entry not found</h3>
        <Link to="/diary" className="inline-block text-xs font-label uppercase tracking-wider text-accent hover:underline">
          Return to Diary
        </Link>
      </div>
    );
  }

  const isOwner = user?.username === log.username;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-6 animate-fade-in pb-16">
      {/* Back button */}
      <Link
        to="/diary"
        className="inline-flex items-center gap-1.5 text-[11px] font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Diary
      </Link>

      {/* Main Log Card */}
      <div className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-5 sm:p-8 space-y-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-border/70 pb-5">
          <div className="space-y-1">
            <Link
              to={`/fragrance/${log.fragrance_id}`}
              className="text-[11px] font-label uppercase tracking-[0.2em] text-accent hover:underline font-semibold inline-flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3 text-accent" />
              <span>{log.house_name}</span>
            </Link>
            <h1 className="font-serif text-2xl sm:text-4xl font-normal text-text-primary leading-tight">
              {log.fragrance_name}
            </h1>
            <p className="font-sans text-xs text-text-secondary pt-0.5">
              Wear logged by <span className="font-medium text-text-primary">@{log.username}</span> on {log.wear_date}
            </p>
          </div>

          {log.is_favorite && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 border border-amber-500/30 rounded text-amber-800 text-xs font-label uppercase tracking-wider font-semibold self-start">
              <Star className="w-3.5 h-3.5 fill-amber-600 text-amber-600" /> Standout Wear
            </div>
          )}
        </div>

        {/* Sensory Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 sm:p-4 bg-surface/50 border border-border/60 rounded-lg sm:rounded">
          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Rating
            </span>
            <div className="flex items-center gap-1.5 pt-0.5">
              <span className="font-serif text-lg sm:text-xl font-semibold text-text-primary">
                {log.rating ? Number(log.rating).toFixed(1) : '—'}
              </span>
              <RatingDots rating={log.rating} size="sm" />
            </div>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary">
              Occasion
            </span>
            <p className="font-sans text-xs sm:text-sm font-medium text-text-primary pt-0.5">{log.occasion || 'Casual'}</p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary flex items-center gap-1">
              <Droplets className="w-3 h-3 text-accent" /> Sprays
            </span>
            <p className="font-sans text-xs sm:text-sm font-medium text-text-primary pt-0.5">{log.sprays || 3} sprays</p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary flex items-center gap-1">
              <Clock className="w-3 h-3 text-accent" /> Longevity
            </span>
            <p className="font-sans text-xs sm:text-sm font-medium text-text-primary pt-0.5">
              {log.longevity_hours ? `${log.longevity_hours} hours` : '—'}
            </p>
          </div>
        </div>

        {/* Review observation text */}
        {log.review_text && (
          <div className="space-y-2 pt-1">
            <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
              Observations & Evolution
            </h3>
            <p className="font-sans text-sm text-text-primary leading-relaxed whitespace-pre-line bg-surface/30 p-4 border border-border/60 rounded italic">
              "{log.review_text}"
            </p>
          </div>
        )}

        {/* Likes / Community appreciation */}
        <div className="flex items-center gap-2 text-xs font-sans text-text-secondary pt-1">
          <Heart className="w-3.5 h-3.5 text-accent fill-accent" />
          <span>{log.like_count} curators found this impression helpful</span>
        </div>

        {/* Owner actions */}
        {isOwner && (
          <div className="pt-4 border-t border-border/60 flex justify-end gap-3">
            <Button variant="danger" size="sm" onClick={handleDelete} className="w-full sm:w-auto">
              <Trash2 className="w-3.5 h-3.5" /> Delete Entry
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
