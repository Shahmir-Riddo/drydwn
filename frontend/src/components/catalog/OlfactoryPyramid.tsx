import React from 'react';
import { Link } from 'react-router-dom';
import type { Note } from '../../types';

export interface OlfactoryPyramidProps {
  topNotes: Note[];
  heartNotes: Note[];
  baseNotes: Note[];
}

export const OlfactoryPyramid: React.FC<OlfactoryPyramidProps> = ({
  topNotes,
  heartNotes,
  baseNotes,
}) => {
  const sections = [
    { label: 'Top Notes (Opening)', notes: topNotes, hint: 'First 15–30 minutes' },
    { label: 'Heart Notes (Body)', notes: heartNotes, hint: '2–4 hours wear' },
    { label: 'Base Notes (Drydown)', notes: baseNotes, hint: 'Final skin impression (4–12+ hours)' },
  ];

  const hasAnyNotes = topNotes.length > 0 || heartNotes.length > 0 || baseNotes.length > 0;

  if (!hasAnyNotes) {
    return (
      <div className="py-6 text-center text-xs text-text-secondary">
        Olfactory notes breakdown not currently catalogued for this composition.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {sections.map((sec) => (
        <div key={sec.label} className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-[11px] font-label uppercase tracking-[0.2em] font-semibold text-text-primary">
              {sec.label}
            </h4>
            <span className="text-[10px] font-sans text-text-secondary/70">{sec.hint}</span>
          </div>

          {sec.notes.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {sec.notes.map((note) => (
                <Link
                  key={note.id}
                  to={`/notes/${note.id}`}
                  className="px-2.5 py-1 bg-surface hover:bg-surface/80 border border-border/80 rounded text-xs text-text-primary hover:border-accent hover:text-accent transition-colors"
                >
                  {note.name}
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-xs text-text-secondary/50 italic">None specified</p>
          )}
        </div>
      ))}
    </div>
  );
};
