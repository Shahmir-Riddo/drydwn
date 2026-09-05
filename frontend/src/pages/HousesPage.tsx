import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import { Input } from '../components/common/Input';
import { Pagination } from '../components/common/Pagination';
import { Compass } from 'lucide-react';

export const HousesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['houses', search, page],
    queryFn: () => catalogApi.getHouses({ q: search || undefined, page }),
  });

  const houses = data?.results || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
        <div>
          <span className="text-[11px] font-label font-semibold uppercase tracking-[0.25em] text-accent">
            Directory
          </span>
          <h1 className="font-serif text-3xl font-normal text-text-primary tracking-tight mt-1">
            Perfume Houses & Brands
          </h1>
          <p className="font-sans text-xs text-text-secondary mt-0.5">
            Discover design houses, indie perfumers, and historic olfactory ateliers.
          </p>
        </div>

        <div className="w-full sm:w-64">
          <Input
            placeholder="Filter houses..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </div>

      {/* House Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-24 bg-surface animate-pulse rounded" />
          ))}
        </div>
      ) : houses.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {houses.map((house) => (
            <Link
              key={house.id}
              to={`/houses/${house.id}`}
              className="vault-card p-5 hover:border-accent/60 transition-all flex items-center justify-between group"
            >
              <div className="space-y-1 min-w-0">
                <h3 className="font-serif text-lg text-text-primary group-hover:text-accent transition-colors truncate">
                  {house.name}
                </h3>
                <p className="text-[11px] font-label uppercase tracking-wider text-text-secondary">
                  {house.fragrance_count} catalogued {house.fragrance_count === 1 ? 'scent' : 'scents'}
                </p>
              </div>
              <Compass className="w-5 h-5 text-border group-hover:text-accent transition-colors shrink-0" />
            </Link>
          ))}
        </div>
      ) : (
        <div className="py-16 text-center text-xs text-text-secondary">
          No perfume houses found matching "{search}".
        </div>
      )}

      {/* Pagination */}
      {data && (
        <Pagination
          currentPage={page}
          totalPages={Math.ceil((data.count || 0) / 30)}
          totalCount={data.count}
          pageSize={30}
          onPageChange={setPage}
          itemLabel="Houses"
        />
      )}
    </div>
  );
};
