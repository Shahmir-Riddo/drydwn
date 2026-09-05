import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountsApi } from '../api/accounts';
import { Input } from '../components/common/Input';
import { UserPlus, Star } from 'lucide-react';

export const FeedPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['feed', searchQuery],
    queryFn: () => accountsApi.getFeed({ q: searchQuery || undefined }),
  });

  const feedItems = data?.feed || [];
  const discoverUsers = data?.discover_users || [];
  const searchResults = data?.search_results || [];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Curator Community
          </span>
          <h1 className="font-serif text-3xl font-normal text-text-primary tracking-tight mt-1">
            Social Activity Feed
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Discover what fellow collectors are logging, rating, and adding to their wardrobe.
          </p>
        </div>

        <div className="w-full sm:w-64">
          <Input
            placeholder="Find curators..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Member Search Results if active */}
      {searchQuery.trim() && (
        <div className="space-y-3">
          <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
            Member Search ({searchResults.length})
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {searchResults.map((u) => (
              <Link
                key={u.username}
                to={`/profile/${u.username}`}
                className="vault-card p-3 flex items-center gap-3 hover:border-accent transition-all"
              >
                <div className="w-9 h-9 rounded-full bg-surface border border-sand flex items-center justify-center font-serif text-sm font-semibold text-text-primary shrink-0">
                  {u.display_name ? u.display_name.substring(0, 2).toUpperCase() : u.username.substring(0, 2).toUpperCase()}
                </div>
                <div className="min-w-0">
                  <p className="font-sans text-xs font-semibold text-text-primary truncate">
                    {u.display_name || u.username}
                  </p>
                  <p className="text-[10px] text-text-secondary">@{u.username}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Feed Layout: Feed Stream (Left) + Discover Curators (Right) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Main Activity Feed */}
        <div className="md:col-span-8 space-y-4">
          <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
            Recent Circle Activity
          </h3>

          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-28 bg-surface animate-pulse rounded" />
              ))}
            </div>
          ) : feedItems.length > 0 ? (
            feedItems.map((item, index) => (
              <div key={index} className="vault-card p-4 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <Link
                    to={`/profile/${item.username}`}
                    className="font-sans font-semibold text-text-primary hover:text-accent flex items-center gap-2"
                  >
                    <div className="w-6 h-6 rounded-full bg-surface border border-sand flex items-center justify-center text-[10px]">
                      {item.display_name ? item.display_name[0].toUpperCase() : item.username[0].toUpperCase()}
                    </div>
                    <span>{item.display_name || item.username}</span>
                  </Link>

                  <span className="text-[10px] text-text-secondary">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </span>
                </div>

                <div className="pl-8 space-y-1">
                  <p className="text-xs text-text-secondary">
                    {item.type === 'wear' ? (
                      <>
                        Logged a wear session for{' '}
                        <Link
                          to={`/fragrance/${item.fragrance_id}`}
                          className="font-serif text-sm font-medium text-text-primary hover:text-accent"
                        >
                          {item.fragrance_name}
                        </Link>{' '}
                        {item.occasion ? `· ${item.occasion}` : ''}
                      </>
                    ) : (
                      <>
                        Added{' '}
                        <Link
                          to={`/fragrance/${item.fragrance_id}`}
                          className="font-serif text-sm font-medium text-text-primary hover:text-accent"
                        >
                          {item.fragrance_name}
                        </Link>{' '}
                        to their <strong className="text-accent">{item.shelf}</strong> shelf
                      </>
                    )}
                  </p>

                  {item.rating && (
                    <div className="flex items-center gap-1 text-[11px] text-accent font-semibold pt-1">
                      <Star className="w-3 h-3 fill-accent" /> Rating: {item.rating} / 5.0
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="py-12 text-center text-xs text-text-secondary bg-surface/30 rounded border border-border/60">
              No recent activity in your circle. Follow curators to see their wear logs here!
            </div>
          )}
        </div>

        {/* Discover Curators Sidebar */}
        <div className="md:col-span-4 space-y-4">
          <h3 className="text-xs font-label uppercase tracking-widest text-text-secondary font-semibold">
            Suggested Curators
          </h3>

          <div className="space-y-2">
            {discoverUsers.map((curator) => (
              <Link
                key={curator.username}
                to={`/profile/${curator.username}`}
                className="vault-card p-3 flex items-center justify-between hover:border-accent transition-all block group"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-full bg-surface border border-sand flex items-center justify-center font-serif text-xs font-semibold text-text-primary shrink-0">
                    {curator.display_name ? curator.display_name.substring(0, 2).toUpperCase() : curator.username.substring(0, 2).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <p className="font-sans text-xs font-semibold text-text-primary group-hover:text-accent transition-colors truncate">
                      {curator.display_name || curator.username}
                    </p>
                    <p className="text-[10px] text-text-secondary truncate">@{curator.username}</p>
                  </div>
                </div>

                <UserPlus className="w-3.5 h-3.5 text-text-secondary group-hover:text-accent transition-colors shrink-0" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
