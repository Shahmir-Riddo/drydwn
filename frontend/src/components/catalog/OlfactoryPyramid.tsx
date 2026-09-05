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
    {
      tier: '01',
      label: 'Top Notes',
      sublabel: 'Opening Volatility',
      hint: '0 – 30 min',
      notes: topNotes,
      borderAccent: 'border-l-accent/40',
      tagBg: 'bg-amber-500/5 text-amber-800 border-amber-500/20',
    },
    {
      tier: '02',
      label: 'Heart Notes',
      sublabel: 'Core Body',
      hint: '30 min – 4 hrs',
      notes: heartNotes,
      borderAccent: 'border-l-accent/70',
      tagBg: 'bg-accent/5 text-accent border-accent/20',
    },
    {
      tier: '03',
      label: 'Base Notes',
      sublabel: 'The Drydown',
      hint: '4 – 12+ hrs',
      notes: baseNotes,
      borderAccent: 'border-l-accent',
      tagBg: 'bg-espresso/5 text-espresso border-espresso/20',
    },
  ];

  const hasAnyNotes = topNotes.length > 0 || heartNotes.length > 0 || baseNotes.length > 0;

  if (!hasAnyNotes) {
    return (
      <div className="py-6 text-center text-xs text-text-secondary bg-surface/30 rounded border border-border/60">
        Olfactory notes breakdown not catalogued yet for this formulation.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-1 border-b border-border/40">
        <h4 className="text-[11px] font-label uppercase tracking-[0.22em] font-semibold text-text-primary">
          Olfactory Deconstruction
        </h4>
        <span className="text-[10px] font-label uppercase tracking-wider text-text-secondary/70">
          3-Tier Evolution
        </span>
      </div>

      <div className="space-y-3">
        {sections.map((sec) => (
          <div
            key={sec.label}
            className={`p-3.5 bg-surface/30 border border-border/60 rounded-sm ${sec.borderAccent} border-l-2 transition-all hover:bg-surface/50`}
          >
            {/* Header row */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-label text-[10px] font-bold tracking-wider text-accent uppercase">
                  {sec.tier}
                </span>
                <span className="text-xs font-semibold text-text-primary font-sans">
                  {sec.label}
                </span>
                <span className="hidden sm:inline text-[10px] text-text-secondary/60">
                  · {sec.sublabel}
                </span>
              </div>
              <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary bg-white px-2 py-0.5 rounded border border-border/50">
                {sec.hint}
              </span>
            </div>

            {/* Note Chips */}
            {sec.notes.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {sec.notes.map((note) => (
                  <Link
                    key={note.id}
                    to={`/notes/${note.id}`}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white hover:bg-surface border border-border/80 rounded text-xs text-text-primary hover:border-accent hover:text-accent transition-all duration-150 active:scale-95 shadow-[0_1px_2px_rgba(0,0,0,0.02)]"
                  >
                    <span className="w-1 h-1 rounded-full bg-accent/60" />
                    <span>{note.name}</span>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-xs text-text-secondary/50 italic pt-0.5">None specified</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
