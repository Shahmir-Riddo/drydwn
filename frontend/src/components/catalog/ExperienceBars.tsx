import React, { useState } from 'react';
import { catalogApi } from '../../api/catalog';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Check } from 'lucide-react';
import type { CommunityInsightCategory } from '../../types';

export interface ExperienceBarsProps {
  fragranceId: number;
  categories: CommunityInsightCategory[];
  totalVoters: number;
  onVoteSuccess?: (newCategories: CommunityInsightCategory[], totalVoters: number) => void;
}

export const ExperienceBars: React.FC<ExperienceBarsProps> = ({
  fragranceId,
  categories,
  totalVoters,
  onVoteSuccess,
}) => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [votingKey, setVotingKey] = useState<string | null>(null);

  const handleVote = async (categoryKey: string, choiceName: string) => {
    if (!isAuthenticated) {
      showToast('Please sign in to cast your experience vote', 'info');
      return;
    }

    setVotingKey(`${categoryKey}-${choiceName}`);
    try {
      const res = await catalogApi.voteFragrance(fragranceId, {
        category: categoryKey,
        choice: choiceName,
      });
      showToast(`Voted "${choiceName}" for ${categoryKey.replace(/_/g, ' ')}`, 'success');
      onVoteSuccess?.(res.insights, res.total_voters);
    } catch {
      showToast('Failed to record vote. Please try again.', 'error');
    } finally {
      setVotingKey(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-serif text-xl font-normal text-text-primary">
            How Users Experience This Fragrance
          </h3>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Community perception aggregated from {totalVoters} curator votes. Click any option to vote.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((cat) => (
          <div key={cat.key} className="vault-card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-label font-semibold uppercase tracking-[0.2em] text-text-primary">
                {cat.title}
              </span>
              <span className="text-[10px] font-sans text-text-secondary">
                {cat.total_votes} votes
              </span>
            </div>

            <div className="space-y-2">
              {cat.options.map((opt) => {
                const isSelected = opt.is_user_choice;
                const isCurrentlyVoting = votingKey === `${cat.key}-${opt.name}`;

                return (
                  <button
                    key={opt.name}
                    type="button"
                    onClick={() => handleVote(cat.key, opt.name)}
                    disabled={isCurrentlyVoting}
                    className={`w-full text-left p-2 rounded-sm border transition-all duration-200 relative overflow-hidden group ${
                      isSelected
                        ? 'border-accent/80 bg-accent/[0.04]'
                        : 'border-border/60 hover:border-border bg-white hover:bg-surface/50'
                    }`}
                  >
                    {/* Background Progress bar */}
                    <div
                      className={`absolute top-0 bottom-0 left-0 transition-all duration-500 ease-luxury ${
                        isSelected ? 'bg-accent/15' : 'bg-surface group-hover:bg-sand/30'
                      }`}
                      style={{ width: `${opt.percentage}%` }}
                    />

                    {/* Content overlay */}
                    <div className="relative z-10 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5 font-medium text-text-primary">
                        {isSelected && <Check className="w-3.5 h-3.5 text-accent" />}
                        <span>{opt.name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-text-secondary text-[11px]">
                        <span>{opt.count}</span>
                        <span className="font-semibold font-label">{opt.percentage}%</span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
