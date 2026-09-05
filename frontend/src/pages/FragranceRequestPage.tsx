import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { catalogApi } from '../api/catalog';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Send } from 'lucide-react';
import type { FragranceRequestItem } from '../types';

export const FragranceRequestPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedGender, setSelectedGender] = useState<'Unisex' | 'Men' | 'Women'>('Unisex');

  const { data: requests, refetch, isLoading } = useQuery({
    queryKey: ['fragrance-requests'],
    queryFn: () => catalogApi.getFragranceRequests(),
    enabled: isAuthenticated,
  });

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<Partial<FragranceRequestItem>>({
    defaultValues: {
      gender: 'Unisex',
    },
  });

  const currentNotes = watch('notes_description') || '';

  const addQuickNote = (noteName: string) => {
    const trimmed = currentNotes.trim();
    if (!trimmed) {
      setValue('notes_description', noteName);
    } else if (!trimmed.toLowerCase().includes(noteName.toLowerCase())) {
      setValue('notes_description', `${trimmed}, ${noteName}`);
    }
  };

  const onSubmit = async (data: Partial<FragranceRequestItem>) => {
    if (!isAuthenticated) {
      showToast('Please sign in to submit a fragrance sourcing request', 'info');
      return;
    }

    setIsSubmitting(true);
    try {
      await catalogApi.submitFragranceRequest({
        ...data,
        gender: selectedGender,
      });
      showToast(`Request for "${data.fragrance_name}" submitted for vault curation`, 'success');
      reset();
      refetch();
    } catch {
      showToast('Failed to submit request', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const popularNotes = ['Amber', 'Bergamot', 'Vanilla', 'Iris', 'Oud', 'Sandalwood', 'Rose', 'Cardamom', 'Vetiver'];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-8 animate-fade-in pb-16">
      {/* Editorial Header */}
      <div className="border-b border-border/80 pb-5 sm:pb-6 space-y-1">
        <div className="flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          <span className="text-[10px] sm:text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Vault Sourcing & Commission
          </span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-normal text-text-primary">
          Request a Fragrance
        </h1>
        <p className="font-sans text-xs text-text-secondary">
          Notice a missing niche, indie, or vintage composition? Submit it to the vault archive for curation.
        </p>
      </div>

      {/* Submission Form Card */}
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white border border-border/80 rounded-xl sm:rounded-sm p-5 sm:p-8 space-y-5 shadow-xs">
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Fragrance Name *"
              placeholder="e.g. Grand Soir"
              {...register('fragrance_name', { required: 'Fragrance name is required' })}
              error={errors.fragrance_name?.message}
            />

            <Input
              label="House / Perfume Brand *"
              placeholder="e.g. Maison Francis Kurkdjian"
              {...register('house_name', { required: 'House name is recommended' })}
            />
          </div>

          {/* Target Audience Segmented Buttons */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
              Target Audience
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['Unisex', 'Men', 'Women'] as const).map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => {
                    setSelectedGender(g);
                    setValue('gender', g);
                  }}
                  className={`py-2 rounded text-xs font-label uppercase tracking-wider border transition-all ${
                    selectedGender === g
                      ? 'bg-text-primary text-white border-text-primary font-semibold shadow-xs'
                      : 'bg-white border-border text-text-secondary hover:border-accent/40'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          {/* Release Year */}
          <Input
            label="Release Year"
            type="number"
            placeholder="e.g. 2016"
            {...register('release_year', { valueAsNumber: true })}
          />

          {/* Notes & Olfactory Breakdown with Quick Add Chips */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
                Known Notes & Olfactory Breakdown
              </label>
              <span className="text-[10px] text-text-secondary/70">Tap tags to add</span>
            </div>
            <textarea
              rows={3}
              placeholder="Amber, vanilla, tonka bean, benzoin, labdanum, cedar..."
              className="form-input text-xs"
              {...register('notes_description')}
            />

            {/* Quick note tags */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {popularNotes.map((note) => (
                <button
                  key={note}
                  type="button"
                  onClick={() => addQuickNote(note)}
                  className="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-surface hover:bg-surface/80 text-text-secondary border border-border/70 hover:border-accent transition-colors"
                >
                  + {note}
                </button>
              ))}
            </div>
          </div>

          {/* Reference URL */}
          <Input
            label="Reference URL (Official House or Database)"
            placeholder="https://www.franciskurkdjian.com/..."
            {...register('reference_url')}
            helperText="Official product link or database entry for validation."
          />
        </div>

        <div className="pt-3 border-t border-border/60">
          <Button
            type="submit"
            variant="accent"
            size="lg"
            isLoading={isSubmitting}
            className="w-full sm:w-auto text-xs tracking-wider"
          >
            <Send className="w-3.5 h-3.5" /> Submit for Curation Review
          </Button>
        </div>
      </form>

      {/* Recent Submissions Feed */}
      {isAuthenticated && (
        <div className="space-y-3.5 pt-4">
          <div className="flex items-center justify-between border-b border-border/60 pb-2">
            <h3 className="text-[11px] font-label uppercase tracking-[0.2em] text-text-secondary font-semibold">
              Recent Vault Sourcing Requests
            </h3>
            <span className="text-[10px] font-sans text-text-secondary/70">
              {requests?.length || 0} Submissions
            </span>
          </div>

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 bg-surface animate-pulse rounded-lg" />
              ))}
            </div>
          ) : requests && requests.length > 0 ? (
            <div className="space-y-2.5">
              {requests.map((req) => (
                <div
                  key={req.id}
                  className="bg-white border border-border/80 rounded-lg p-3.5 sm:p-4 flex items-center justify-between gap-3 text-xs shadow-xs"
                >
                  <div className="space-y-0.5">
                    <h4 className="font-serif text-base text-text-primary font-medium leading-snug">
                      {req.fragrance_name}
                      {req.house_name && (
                        <span className="text-text-secondary font-sans text-xs ml-1.5 font-normal">
                          · {req.house_name}
                        </span>
                      )}
                    </h4>
                    <p className="text-[10px] sm:text-[11px] text-text-secondary/80 flex items-center gap-1.5 pt-0.5">
                      <span>Submitted by @{req.username}</span>
                      <span>·</span>
                      <span>{new Date(req.created_at).toLocaleDateString()}</span>
                    </p>
                  </div>

                  <span
                    className={`text-[9px] sm:text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded font-semibold shrink-0 ${
                      req.status === 'Added'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : req.status === 'Approved'
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {req.status || 'Pending'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-text-secondary bg-surface/30 rounded border border-border/60">
              No community submissions currently pending review.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
