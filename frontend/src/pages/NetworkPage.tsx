import React from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountsApi } from '../api/accounts';
import { ArrowLeft } from 'lucide-react';

export const NetworkPage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const location = useLocation();
  const isFollowers = location.pathname.includes('/followers');

  const { data: users, isLoading } = useQuery({
    queryKey: ['network', username, isFollowers ? 'followers' : 'following'],
    queryFn: () => {
      if (isFollowers) {
        return accountsApi.getFollowers(username!);
      }
      return accountsApi.getFollowing(username!);
    },
    enabled: !!username,
  });

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8 animate-fade-in">
      <Link
        to={`/profile/${username}`}
        className="inline-flex items-center gap-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to @{username} Dossier
      </Link>

      <div className="border-b border-border/80 pb-6 space-y-1">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
          Curator Network
        </span>
        <h1 className="font-serif text-3xl font-normal text-text-primary">
          {isFollowers ? 'Followers' : 'Following'} ({users?.length || 0})
        </h1>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-16 bg-surface animate-pulse rounded" />
          ))}
        </div>
      ) : users && users.length > 0 ? (
        <div className="divide-y divide-border/60">
          {users.map((u) => (
            <div key={u.username} className="py-3.5 flex items-center justify-between gap-4">
              <Link to={`/profile/${u.username}`} className="flex items-center gap-3 min-w-0 group">
                {u.avatar_url ? (
                  <img
                    src={u.avatar_url}
                    alt={u.display_name || u.username}
                    className="w-10 h-10 rounded-full object-cover border border-sand shrink-0"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-surface border border-sand flex items-center justify-center font-serif text-sm font-semibold text-text-primary shrink-0">
                    {u.display_name ? u.display_name.substring(0, 2).toUpperCase() : u.username.substring(0, 2).toUpperCase()}
                  </div>
                )}
                <div className="min-w-0">
                  <p className="font-sans text-sm font-medium text-text-primary group-hover:text-accent transition-colors truncate">
                    {u.display_name || u.username}
                  </p>
                  <p className="text-[11px] text-text-secondary truncate">@{u.username}</p>
                </div>
              </Link>

              {u.is_following && (
                <span className="text-[10px] font-label uppercase tracking-widest text-accent bg-accent/10 px-2 py-0.5 rounded font-semibold shrink-0">
                  Following
                </span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="py-12 text-center text-xs text-text-secondary bg-surface/30 rounded border border-border/60">
          No curators found in this list.
        </div>
      )}
    </div>
  );
};
