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
        <div className="pt-2 flex justify-center gap-3">
          <Link to="/login">
            <Button variant="accent">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button variant="outline">Create Vault Account</Button>
          </Link>
        </div>
      </div>
    );
  }

  const logs = data?.results || [];
  const totalLogs = data?.count || 0;
  const standoutCount = logs.filter((l) => l.is_favorite).length;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header & Stats Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Curator Journal · @{user?.username}
          </span>
          <h1 className="font-serif text-3xl font-normal text-text-primary tracking-tight mt-1">
            Scent Diary
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Your chronological wear archive capturing olfactory evolution, projection, and skin performance.
          </p>
        </div>

        <Button variant="accent" onClick={openLogModal}>
          <Plus className="w-3.5 h-3.5" /> Log Wear Session
        </Button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="vault-card p-4 space-y-1">
          <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
            Total Sessions
          </span>
          <p className="font-serif text-2xl text-text-primary">{totalLogs}</p>
        </div>

        <div className="vault-card p-4 space-y-1">
          <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
            Standout Wears
          </span>
          <p className="font-serif text-2xl text-accent flex items-center gap-1.5">
            {standoutCount} <Star className="w-4 h-4 fill-accent" />
          </p>
        </div>

        <div className="vault-card p-4 space-y-1 col-span-2 sm:col-span-1">
          <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
            Diary Status
          </span>
          <p className="font-serif text-2xl text-text-primary">Active</p>
        </div>
      </div>

      {/* Log Feed */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <DiaryLogSkeleton key={i} />
          ))}
        </div>
      ) : logs.length > 0 ? (
        <div className="space-y-4">
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
        <div className="py-16 text-center space-y-4 bg-surface/40 border border-border/60 rounded">
          <BookOpen className="w-8 h-8 text-accent/40 mx-auto" />
          <h3 className="font-serif text-xl text-text-primary">Your Scent Diary is empty</h3>
          <p className="font-sans text-xs text-text-secondary max-w-sm mx-auto">
            Log your first fragrance wear session to begin tracking skin longevity, projection, and daily scent memories.
          </p>
          <Button variant="accent" size="sm" onClick={openLogModal}>
            <Plus className="w-3.5 h-3.5" /> Log Your First Wear
          </Button>
        </div>
      )}
    </div>
  );
};
