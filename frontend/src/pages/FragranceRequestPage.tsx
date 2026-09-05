import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { catalogApi } from '../api/catalog';
import { Input } from '../components/common/Input';
import { Select } from '../components/common/Select';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import type { FragranceRequestItem } from '../types';

export const FragranceRequestPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: requests, refetch, isLoading } = useQuery({
    queryKey: ['fragrance-requests'],
    queryFn: () => catalogApi.getFragranceRequests(),
    enabled: isAuthenticated,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<Partial<FragranceRequestItem>>();

  const onSubmit = async (data: Partial<FragranceRequestItem>) => {
    if (!isAuthenticated) {
      showToast('Please sign in to submit a fragrance request', 'info');
      return;
    }

    setIsSubmitting(true);
    try {
      await catalogApi.submitFragranceRequest(data);
      showToast(`Request for "${data.fragrance_name}" submitted for curation review`, 'success');
      reset();
      refetch();
    } catch {
      showToast('Failed to submit request', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10 animate-fade-in">
      <div className="border-b border-border/80 pb-6 space-y-1">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Vault Curation
        </span>
        <h1 className="font-serif text-3xl font-normal text-text-primary">
          Request a Fragrance
        </h1>
        <p className="font-sans text-xs text-text-secondary">
          Notice a missing niche, indie, or vintage composition? Submit it to the vault archive.
        </p>
      </div>

      {/* Submission Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="vault-card p-6 sm:p-8 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Fragrance Name *"
            placeholder="e.g. Grand Soir"
            {...register('fragrance_name', { required: 'Fragrance name is required' })}
            error={errors.fragrance_name?.message}
          />

          <Input
            label="House / Brand Name"
            placeholder="e.g. Maison Francis Kurkdjian"
            {...register('house_name')}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Select
            label="Target Audience"
            {...register('gender')}
            options={[
              { value: 'Unisex', label: 'Unisex' },
              { value: 'Men', label: 'Men' },
              { value: 'Women', label: 'Women' },
            ]}
          />

          <Input
            label="Release Year"
            type="number"
            placeholder="e.g. 2016"
            {...register('release_year', { valueAsNumber: true })}
          />
        </div>

        <div className="space-y-1.5">
          <label className="block text-[11px] font-label font-medium uppercase tracking-wider text-text-secondary">
            Known Notes & Olfactory Breakdown
          </label>
          <textarea
            rows={3}
            placeholder="Amber, vanilla, tonka bean, benzoin, labdanum..."
            className="form-input"
            {...register('notes_description')}
          />
        </div>

        <Input
          label="Reference URL"
          placeholder="https://www.fragrantica.com/perfume/..."
          {...register('reference_url')}
          helperText="Link to official house page or Fragrantica for reference."
        />

        <div className="flex justify-end pt-4">
          <Button type="submit" variant="accent" size="lg" isLoading={isSubmitting}>
            Submit Fragrance for Review
          </Button>
        </div>
      </form>

      {/* Recent Submissions */}
      {isAuthenticated && (
        <div className="space-y-4 pt-6 border-t border-border/80">
          <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
            Recent Community Submissions
          </h3>

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-16 bg-surface animate-pulse rounded" />
              ))}
            </div>
          ) : requests && requests.length > 0 ? (
            <div className="divide-y divide-border/60 vault-card p-4">
              {requests.map((req) => (
                <div key={req.id} className="py-3 flex items-center justify-between gap-4 text-xs">
                  <div>
                    <h4 className="font-serif text-base text-text-primary font-medium">
                      {req.fragrance_name} {req.house_name ? `— ${req.house_name}` : ''}
                    </h4>
                    <p className="text-[11px] text-text-secondary">
                      Submitted by @{req.username} on {new Date(req.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <span
                    className={`text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded font-semibold ${
                      req.status === 'Added'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : req.status === 'Approved'
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'bg-surface text-text-secondary border border-border'
                    }`}
                  >
                    {req.status}
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
