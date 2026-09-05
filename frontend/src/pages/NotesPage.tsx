import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import { Input } from '../components/common/Input';
import { Pagination } from '../components/common/Pagination';

export const NotesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['notes', search, page],
    queryFn: () => catalogApi.getNotes({ q: search || undefined, page }),
  });

  const notes = data?.results || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Olfactory Vocabulary
          </span>
          <h1 className="font-serif text-3xl font-normal text-text-primary tracking-tight mt-1">
            Fragrance Notes
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Explore natural isolates, aroma molecules, and classic perfume accords.
          </p>
        </div>

        <div className="w-full sm:w-64">
          <Input
            placeholder="Search notes (e.g. Bergamot, Iris)..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </div>

      {/* Notes Grid */}
      {isLoading ? (
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 40 }).map((_, i) => (
            <div key={i} className="h-8 w-24 bg-surface animate-pulse rounded" />
          ))}
        </div>
      ) : notes.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {notes.map((note) => (
            <Link
              key={note.id}
              to={`/notes/${note.id}`}
              className="px-3.5 py-1.5 bg-white hover:bg-surface border border-border rounded text-xs text-text-primary hover:border-accent hover:text-accent transition-all font-sans"
            >
              {note.name}
            </Link>
          ))}
        </div>
      ) : (
        <div className="py-16 text-center text-xs text-text-secondary">
          No fragrance notes found matching "{search}".
        </div>
      )}

      {/* Pagination */}
      {data && (
        <Pagination
          currentPage={page}
          totalPages={Math.ceil((data.count || 0) / 50)}
          totalCount={data.count}
          pageSize={50}
          onPageChange={setPage}
          itemLabel="Notes"
        />
      )}
    </div>
  );
};
