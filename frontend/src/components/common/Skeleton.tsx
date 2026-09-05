import React from 'react';
import { clsx } from 'clsx';

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => {
  return <div className={clsx('bg-surface animate-pulse rounded-sm', className)} />;
};

export const FragranceCardSkeleton: React.FC = () => {
  return (
    <div className="vault-card p-4 space-y-3">
      <div className="w-full aspect-[3/4] bg-surface animate-pulse rounded-sm flex items-center justify-center">
        <div className="w-16 h-28 bg-sand/30 rounded-sm" />
      </div>
      <div className="space-y-1.5 pt-1">
        <Skeleton className="h-2.5 w-16" />
        <Skeleton className="h-4 w-3/4" />
        <div className="flex justify-between pt-1">
          <Skeleton className="h-3 w-12" />
          <Skeleton className="h-3 w-8" />
        </div>
      </div>
    </div>
  );
};

export const DiaryLogSkeleton: React.FC = () => {
  return (
    <div className="vault-card p-5 space-y-3">
      <div className="flex justify-between items-start">
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-5 w-48" />
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <Skeleton className="h-12 w-full" />
      <div className="flex gap-4 pt-2 border-t border-border/50">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-3 w-20" />
      </div>
    </div>
  );
};

export const FragranceDetailSkeleton: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-12 gap-8">
      <div className="md:col-span-5 space-y-4">
        <Skeleton className="w-full aspect-[3/4] rounded" />
      </div>
      <div className="md:col-span-7 space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-4 w-1/3" />
        </div>
        <Skeleton className="h-24 w-full" />
        <div className="space-y-3 pt-4">
          <Skeleton className="h-6 w-40" />
          <div className="grid grid-cols-3 gap-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
        </div>
      </div>
    </div>
  );
};
