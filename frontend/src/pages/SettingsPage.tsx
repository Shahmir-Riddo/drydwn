import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { accountsApi } from '../api/accounts';
import { Select } from '../components/common/Select';
import { Button } from '../components/common/Button';
import { useToast } from '../context/ToastContext';
import { Download, Eye, Palette } from 'lucide-react';
import type { UserSettings } from '../types';

export const SettingsPage: React.FC = () => {
  const { showToast } = useToast();
  const [isSaving, setIsSaving] = useState(false);

  const { data: settings, isLoading } = useQuery({
    queryKey: ['user-settings'],
    queryFn: () => accountsApi.getSettings(),
  });

  const { register, handleSubmit, reset } = useForm<UserSettings>();

  useEffect(() => {
    if (settings) {
      reset(settings);
    }
  }, [settings, reset]);

  const onSubmit = async (data: UserSettings) => {
    setIsSaving(true);
    try {
      await accountsApi.updateSettings(data);
      showToast('Preferences successfully saved', 'success');
    } catch {
      showToast('Failed to save settings', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleExport = (format: 'CSV' | 'JSON') => {
    window.location.href = accountsApi.exportData(format);
    showToast(`Downloading your vault archive (${format})...`, 'info');
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4 space-y-6">
        <div className="h-8 w-48 bg-surface animate-pulse rounded" />
        <div className="h-64 bg-surface animate-pulse rounded" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <div className="border-b border-border/80 pb-6 space-y-1">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Preferences & Controls
        </span>
        <h1 className="font-serif text-3xl font-normal text-text-primary">Curator Settings</h1>
        <p className="font-sans text-xs text-text-secondary">
          Configure interface appearance, privacy visibility, and export your personal collection.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Appearance & Interface */}
        <div className="vault-card p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-border/60 pb-3">
            <Palette className="w-4 h-4 text-accent" />
            <h3 className="font-serif text-lg text-text-primary">Appearance & Interface</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label="Visual Theme"
              {...register('theme')}
              options={[
                { value: 'Light', label: 'Warm Cream (Light)' },
                { value: 'Dark', label: 'Tuxedo Dark (Dark)' },
                { value: 'Auto', label: 'System Automatic' },
              ]}
            />

            <Select
              label="Default Wardrobe Shelf"
              {...register('default_shelf')}
              options={[
                { value: 'Owned', label: 'Owned' },
                { value: 'Wishlist', label: 'Wishlist' },
                { value: 'Tried', label: 'Tried' },
                { value: 'Want to Try', label: 'Want to Try' },
              ]}
            />
          </div>
        </div>

        {/* Privacy & Social */}
        <div className="vault-card p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-border/60 pb-3">
            <Eye className="w-4 h-4 text-accent" />
            <h3 className="font-serif text-lg text-text-primary">Privacy & Network</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
              label="Curator Profile Visibility"
              {...register('profile_visibility')}
              options={[
                { value: 'Public', label: 'Public (Discoverable by everyone)' },
                { value: 'Followers Only', label: 'Followers Only' },
                { value: 'Private', label: 'Private (Vault locked)' },
              ]}
            />

            <Select
              label="Bottle Volume Units"
              {...register('bottle_size_unit')}
              options={[
                { value: 'ML', label: 'Milliliters (ml)' },
                { value: 'OZ', label: 'Fluid Ounces (fl oz)' },
              ]}
            />
          </div>
        </div>

        {/* Action button */}
        <div className="flex justify-end">
          <Button type="submit" variant="accent" size="lg" isLoading={isSaving}>
            Save Preferences
          </Button>
        </div>
      </form>

      {/* Data Export Vault Section */}
      <div className="vault-card p-6 space-y-4 border-dashed">
        <div className="flex items-center gap-2 border-b border-border/60 pb-3">
          <Download className="w-4 h-4 text-accent" />
          <h3 className="font-serif text-lg text-text-primary">Data Export & Backup</h3>
        </div>

        <p className="font-sans text-xs text-text-secondary leading-relaxed">
          Download your complete fragrance collection, personal ratings, wear logs, and observation notes as a structured CSV spreadsheet or raw JSON archive.
        </p>

        <div className="flex flex-wrap gap-3 pt-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('CSV')}>
            <Download className="w-3.5 h-3.5" /> Export Collection (CSV)
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('JSON')}>
            <Download className="w-3.5 h-3.5" /> Export Collection (JSON)
          </Button>
        </div>
      </div>
    </div>
  );
};
