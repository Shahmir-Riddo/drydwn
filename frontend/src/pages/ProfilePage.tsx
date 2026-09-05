import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountsApi } from '../api/accounts';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Sparkles, MapPin, Calendar, Edit3, UserCheck, UserPlus, Layers } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const { user: currentUser, isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [isTogglingFollow, setIsTogglingFollow] = useState(false);

  const targetUsername = username || currentUser?.username;

  const { data: profile, isLoading, refetch } = useQuery({
    queryKey: ['profile', targetUsername],
    queryFn: () => {
      if (!username || username === currentUser?.username) {
        return accountsApi.getMyProfile();
      }
      return accountsApi.getProfile(username);
    },
    enabled: !!targetUsername,
  });

  const isOwnProfile = !username || (currentUser && currentUser.username === username);

  const handleToggleFollow = async () => {
    if (!isAuthenticated) {
      showToast('Please sign in to follow curators', 'info');
      return;
    }
    if (!profile) return;

    setIsTogglingFollow(true);
    try {
      const res = await accountsApi.toggleFollow(profile.username);
      showToast(res.detail, 'success');
      refetch();
    } catch {
      showToast('Failed to update follow status', 'error');
    } finally {
      setIsTogglingFollow(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <div className="h-24 bg-surface animate-pulse rounded" />
        <div className="h-48 bg-surface animate-pulse rounded" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-3">
        <h3 className="font-serif text-xl text-text-primary">Curator profile not found</h3>
        <Link to="/" className="text-xs text-accent hover:underline">
          Return to Catalogue
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Curator Header Dossier Card */}
      <div className="vault-card p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            {/* Avatar / Monogram */}
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt={profile.display_name || profile.username}
                className="w-20 h-20 rounded-full object-cover border border-sand shadow-sm shrink-0"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-surface border border-sand flex items-center justify-center font-serif text-2xl font-semibold text-text-primary shrink-0">
                {profile.display_name
                  ? profile.display_name.substring(0, 2).toUpperCase()
                  : profile.username.substring(0, 2).toUpperCase()}
              </div>
            )}

            <div className="space-y-1">
              <span className="text-[10px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
                Vault Curator Dossier
              </span>
              <h1 className="font-serif text-2xl sm:text-3xl font-normal text-text-primary">
                {profile.display_name || profile.username}
              </h1>
              <p className="font-sans text-xs text-text-secondary">@{profile.username}</p>

              <div className="flex flex-wrap items-center gap-4 text-xs text-text-secondary pt-1">
                {profile.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-text-secondary/70" />
                    {profile.location}
                  </span>
                )}
                {profile.created_at && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-text-secondary/70" />
                    Joined {new Date(profile.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Action buttons (Edit Profile or Follow) */}
          <div className="flex items-center gap-3 self-end sm:self-center">
            {isOwnProfile ? (
              <Link to="/profile/edit">
                <Button variant="outline" size="sm">
                  <Edit3 className="w-3.5 h-3.5" /> Edit Dossier
                </Button>
              </Link>
            ) : (
              <Button
                variant={profile.is_following ? 'outline' : 'accent'}
                size="sm"
                onClick={handleToggleFollow}
                isLoading={isTogglingFollow}
              >
                {profile.is_following ? (
                  <>
                    <UserCheck className="w-3.5 h-3.5" /> Following
                  </>
                ) : (
                  <>
                    <UserPlus className="w-3.5 h-3.5" /> Follow Curator
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Bio */}
        {profile.bio && (
          <p className="font-sans text-xs sm:text-sm text-text-secondary leading-relaxed pt-2 border-t border-border/60">
            {profile.bio}
          </p>
        )}

        {/* Network & Signature Fragrance Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-border/60 text-xs">
          {/* Signature Fragrance */}
          <div className="space-y-1">
            <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
              Signature Scent
            </span>
            {profile.favorite_fragrance ? (
              <Link
                to={`/fragrance/${profile.favorite_fragrance.id}`}
                className="font-serif text-sm font-medium text-text-primary hover:text-accent flex items-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5 text-accent" />
                {profile.favorite_fragrance.name}
              </Link>
            ) : (
              <p className="text-text-secondary italic text-xs">None designated</p>
            )}
          </div>

          {/* Followers */}
          <Link
            to={`/profile/${profile.username}/followers`}
            className="space-y-1 hover:text-accent transition-colors block"
          >
            <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
              Followers
            </span>
            <p className="font-serif text-lg font-medium text-text-primary">
              {profile.follower_count}
            </p>
          </Link>

          {/* Following */}
          <Link
            to={`/profile/${profile.username}/following`}
            className="space-y-1 hover:text-accent transition-colors block"
          >
            <span className="text-[10px] font-label uppercase tracking-widest text-text-secondary">
              Following
            </span>
            <p className="font-serif text-lg font-medium text-text-primary">
              {profile.following_count}
            </p>
          </Link>
        </div>
      </div>

      {/* Quick Nav to Wardrobe & Diary */}
      <div className="flex gap-4">
        <Link to="/wardrobe" className="flex-1">
          <div className="vault-card p-5 hover:border-accent transition-all flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Layers className="w-5 h-5 text-accent" />
              <div>
                <h3 className="font-serif text-base text-text-primary">View Full Wardrobe</h3>
                <p className="text-xs text-text-secondary">Explore flacons across collection shelves</p>
              </div>
            </div>
            <span className="text-xs font-label uppercase tracking-wider text-accent">Open →</span>
          </div>
        </Link>
      </div>
    </div>
  );
};
