import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from '../components/common/Button';

export const NoteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: note, isLoading } = useQuery({
    queryKey: ['note', id],
    queryFn: () => catalogApi.getNoteDetail(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-4">
        <div className="h-6 w-24 bg-surface animate-pulse rounded" />
        <div className="h-12 w-48 bg-surface animate-pulse rounded" />
      </div>
    );
  }

  if (!note) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-3">
        <h3 className="font-serif text-xl text-text-primary">Note not found</h3>
        <Link to="/notes" className="text-xs text-accent hover:underline">
          Return to Notes Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <Link
        to="/notes"
        className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Notes
      </Link>

      <div className="vault-card p-8 space-y-4">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Olfactory Element
        </span>
        <h1 className="font-serif text-4xl font-normal text-text-primary">{note.name}</h1>
        <p className="font-sans text-xs text-text-secondary leading-relaxed max-w-lg">
          An essential note element in classical and modern perfumery, used to define structural accords in top, heart, or base drydowns.
        </p>

        <div className="pt-4 flex gap-3">
          <Link to={`/?q=${encodeURIComponent(note.name)}`}>
            <Button variant="accent" size="sm">
              <Sparkles className="w-3.5 h-3.5" /> Find Fragrances with {note.name}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
