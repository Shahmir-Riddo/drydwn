import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useOutletContext } from 'react-router-dom';
import { diaryApi } from '../api/diary';
import { ScentLogCard } from '../components/diary/ScentLogCard';
import { DiaryLogSkeleton } from '../components/common/Skeleton';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Plus, Sparkles, BookOpen, Star } from 'lucide-react';

export const DiaryPage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const { showToast } = useToast();
  const { openLogModal } = useOutletContext<{ openLogModal: () => void }>() || {};
  const [page, setPage] = useState(1);
  const [filterMode, setFilterMode] = useState<'all' | 'standouts'>('all');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['diary-logs', page],
    queryFn: () => diaryApi.getLogs({ page }),
    enabled: isAuthenticated,
  });

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this wear log entry?')) return;
    try {
      await diaryApi.deleteLog(id);
      showToast('Wear log deleted from your diary', 'info');
      refetch();
    } catch {
      showToast('Failed to delete log entry', 'error');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 text-center space-y-4">
        <Sparkles className="w-10 h-10 text-accent/60 mx-auto" />
        <h2 className="font-serif text-2xl text-text-primary">Curator Diary is Private</h2>
        <p className="font-sans text-xs text-text-secondary">
          Sign in to your curator account to view, log, and organize your daily fragrance wear sessions.
        </p>
        <div className="pt-2 flex flex-col sm:flex-row justify-center gap-3">
          <Link to="/login" className="w-full sm:w-auto">
            <Button variant="accent" className="w-full">Sign In</Button>
          </Link>
          <Link to="/register" className="w-full sm:w-auto">
            <Button variant="outline" className="w-full">Create Vault Account</Button>
          </Link>
        </div>
      </div>
    );
  }

  const allLogs = data?.results || [];
  const totalLogs = data?.count || 0;
  const standoutCount = allLogs.filter((l) => l.is_favorite).length;

  const logs = filterMode === 'standouts' ? allLogs.filter((l) => l.is_favorite) : allLogs;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-6 sm:space-y-8 animate-fade-in pb-16">
      {/* Header & Stats Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-5 sm:pb-6">
        <div>
          <span className="text-[10px] sm:text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Curator Journal · @{user?.username}
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-normal text-text-primary tracking-tight mt-1">
            Scent Diary
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Your chronological wear archive capturing olfactory evolution, projection, and skin performance.
          </p>
        </div>

        <Button
          variant="accent"
          onClick={openLogModal}
          className="w-full sm:w-auto py-2.5 text-xs tracking-wider shrink-0"
        >
          <Plus className="w-4 h-4 stroke-[2]" /> Log Wear Session
        </Button>
      </div>

      {/* Summary KPI Dashboard (Refined 3-Pill Layout) */}
      <div className="grid grid-cols-3 gap-2.5 sm:gap-4">
        <div className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-3 sm:p-4 space-y-0.5 text-center sm:text-left shadow-xs">
          <span className="text-[9px] sm:text-[10px] font-label uppercase tracking-widest text-text-secondary block">
            Sessions
          </span>
          <p className="font-serif text-xl sm:text-3xl text-text-primary font-normal">{totalLogs}</p>
        </div>

        <div className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-3 sm:p-4 space-y-0.5 text-center sm:text-left shadow-xs">
          <span className="text-[9px] sm:text-[10px] font-label uppercase tracking-widest text-text-secondary block">
            Standouts
          </span>
          <p className="font-serif text-xl sm:text-3xl text-accent font-normal flex items-center justify-center sm:justify-start gap-1">
            {standoutCount} <Star className="w-3.5 h-3.5 fill-accent" />
          </p>
        </div>

        <div className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-3 sm:p-4 space-y-0.5 text-center sm:text-left shadow-xs">
          <span className="text-[9px] sm:text-[10px] font-label uppercase tracking-widest text-text-secondary block">
            Archive
          </span>
          <p className="font-serif text-xl sm:text-3xl text-text-primary font-normal">Active</p>
        </div>
      </div>

      {/* Filter Tabs Bar */}
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <button
            onClick={() => setFilterMode('all')}
            className={`px-3 py-1 rounded text-xs font-label uppercase tracking-wider transition-colors ${
              filterMode === 'all'
                ? 'bg-text-primary text-white font-semibold'
                : 'text-text-secondary hover:text-text-primary bg-surface/60'
            }`}
          >
            All Logs ({totalLogs})
          </button>
          <button
            onClick={() => setFilterMode('standouts')}
            className={`px-3 py-1 rounded text-xs font-label uppercase tracking-wider transition-colors inline-flex items-center gap-1 ${
              filterMode === 'standouts'
                ? 'bg-accent text-white font-semibold'
                : 'text-text-secondary hover:text-accent bg-surface/60'
            }`}
          >
            <Star className="w-3 h-3 fill-current" /> Standouts ({standoutCount})
          </button>
        </div>

        <span className="text-[11px] font-sans text-text-secondary/80">
          Page {page}
        </span>
      </div>

      {/* Log Feed */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <DiaryLogSkeleton key={i} />
          ))}
        </div>
      ) : logs.length > 0 ? (
        <div className="space-y-3.5 sm:space-y-4">
          {logs.map((log) => (
            <ScentLogCard
              key={log.id}
              log={log}
              onDelete={handleDelete}
              showActions
            />
          ))}

          {/* Pagination */}
          {data && (data.next || data.previous) && (
            <div className="flex justify-between items-center pt-6">
              <Button
                variant="outline"
                size="sm"
                disabled={!data.previous}
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              >
                ← Newer Logs
              </Button>
              <span className="text-xs text-text-secondary font-label uppercase tracking-wider">
                Page {page}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={!data.next}
                onClick={() => setPage((prev) => prev + 1)}
              >
                Older Logs →
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="py-16 px-4 text-center space-y-4 bg-surface/30 border border-border/60 rounded-xl sm:rounded-sm">
          <BookOpen className="w-8 h-8 text-accent/40 mx-auto" />
          <h3 className="font-serif text-xl text-text-primary">
            {filterMode === 'standouts' ? 'No standout wears flagged yet' : 'Your Scent Diary is empty'}
          </h3>
          <p className="font-sans text-xs text-text-secondary max-w-sm mx-auto">
            {filterMode === 'standouts'
              ? 'Mark any memorable daily wear as a standout to showcase it here.'
              : 'Log your first fragrance wear session to begin tracking skin longevity, projection, and daily scent memories.'}
          </p>
          <Button variant="accent" size="sm" onClick={openLogModal}>
            <Plus className="w-3.5 h-3.5" /> Log Wear Session
          </Button>
        </div>
      )}
    </div>
  );
};
