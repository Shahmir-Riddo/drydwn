import React from 'react';
import { clsx } from 'clsx';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalCount?: number;
  pageSize?: number;
  siblingCount?: number;
  disabled?: boolean;
  className?: string;
  showItemCount?: boolean;
  itemLabel?: string;
}

const generatePagination = (currentPage: number, totalPages: number, siblingCount = 1): (number | string)[] => {
  const totalNumbers = siblingCount * 2 + 5; // 1 + dots + siblings + current + siblings + dots + total

  if (totalPages <= totalNumbers) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
  const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

  const shouldShowLeftDots = leftSiblingIndex > 2;
  const shouldShowRightDots = rightSiblingIndex < totalPages - 1;

  if (!shouldShowLeftDots && shouldShowRightDots) {
    const leftItemCount = 3 + 2 * siblingCount;
    const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
    return [...leftRange, '...', totalPages];
  }

  if (shouldShowLeftDots && !shouldShowRightDots) {
    const rightItemCount = 3 + 2 * siblingCount;
    const rightRange = Array.from({ length: rightItemCount }, (_, i) => totalPages - rightItemCount + i + 1);
    return [1, '...', ...rightRange];
  }

  const middleRange = Array.from(
    { length: rightSiblingIndex - leftSiblingIndex + 1 },
    (_, i) => leftSiblingIndex + i
  );
  return [1, '...', ...middleRange, '...', totalPages];
};

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  totalCount,
  pageSize = 24,
  siblingCount = 1,
  disabled = false,
  className,
  showItemCount = true,
  itemLabel = 'Compositions',
}) => {
  if (totalPages <= 1 && (!totalCount || totalCount <= pageSize)) {
    return null;
  }

  const paginationRange = generatePagination(currentPage, totalPages, siblingCount);

  const startItem = totalCount ? (currentPage - 1) * pageSize + 1 : 0;
  const endItem = totalCount ? Math.min(currentPage * pageSize, totalCount) : 0;

  const handlePageClick = (page: number) => {
    if (page === currentPage || page < 1 || page > totalPages || disabled) return;
    onPageChange(page);
  };

  return (
    <nav
      aria-label="Pagination Navigation"
      className={clsx(
        'flex flex-col sm:flex-row items-center justify-between gap-4 pt-8 pb-4 border-t border-border/80',
        className
      )}
    >
      {/* Item count status summary */}
      {showItemCount && totalCount !== undefined && totalCount > 0 && (
        <div className="text-[11px] font-label uppercase tracking-widest text-text-secondary">
          Showing <span className="font-semibold text-text-primary">{startItem.toLocaleString()}–{endItem.toLocaleString()}</span> of{' '}
          <span className="font-semibold text-text-primary">{totalCount.toLocaleString()}</span> {itemLabel}
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center gap-1.5 sm:gap-2">
        {/* First Page Button */}
        {totalPages > 5 && (
          <button
            type="button"
            onClick={() => handlePageClick(1)}
            disabled={currentPage === 1 || disabled}
            aria-label="Go to first page"
            className="hidden sm:inline-flex items-center justify-center w-8 h-8 rounded border border-border bg-white hover:bg-surface hover:border-accent hover:text-accent disabled:opacity-40 disabled:pointer-events-none text-text-secondary transition-all text-xs"
            title="First page"
          >
            <ChevronsLeft className="w-3.5 h-3.5" />
          </button>
        )}

        {/* Previous Page Button */}
        <button
          type="button"
          onClick={() => handlePageClick(currentPage - 1)}
          disabled={currentPage === 1 || disabled}
          aria-label="Go to previous page"
          className="inline-flex items-center justify-center gap-1 px-2.5 sm:px-3 h-8 rounded border border-border bg-white hover:bg-surface hover:border-accent hover:text-accent disabled:opacity-40 disabled:pointer-events-none text-text-secondary transition-all text-xs font-label uppercase tracking-wider"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Prev</span>
        </button>

        {/* Numbered Page Pills */}
        <div className="flex items-center gap-1">
          {paginationRange.map((pageNumber, idx) => {
            if (pageNumber === '...') {
              return (
                <span
                  key={`dots-${idx}`}
                  className="w-7 sm:w-8 h-8 flex items-center justify-center text-xs text-text-secondary select-none font-label"
                >
                  …
                </span>
              );
            }

            const page = pageNumber as number;
            const isActive = page === currentPage;

            return (
              <button
                key={`page-${page}`}
                type="button"
                onClick={() => handlePageClick(page)}
                disabled={disabled}
                aria-current={isActive ? 'page' : undefined}
                aria-label={`Page ${page}`}
                className={clsx(
                  'w-7 sm:w-8 h-8 rounded text-xs font-label uppercase transition-all flex items-center justify-center',
                  isActive
                    ? 'bg-accent text-white font-semibold shadow-2xs border border-accent'
                    : 'border border-border bg-white text-text-primary hover:border-accent hover:text-accent hover:bg-surface'
                )}
              >
                {page}
              </button>
            );
          })}
        </div>

        {/* Next Page Button */}
        <button
          type="button"
          onClick={() => handlePageClick(currentPage + 1)}
          disabled={currentPage === totalPages || disabled}
          aria-label="Go to next page"
          className="inline-flex items-center justify-center gap-1 px-2.5 sm:px-3 h-8 rounded border border-border bg-white hover:bg-surface hover:border-accent hover:text-accent disabled:opacity-40 disabled:pointer-events-none text-text-secondary transition-all text-xs font-label uppercase tracking-wider"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>

        {/* Last Page Button */}
        {totalPages > 5 && (
          <button
            type="button"
            onClick={() => handlePageClick(totalPages)}
            disabled={currentPage === totalPages || disabled}
            aria-label="Go to last page"
            className="hidden sm:inline-flex items-center justify-center w-8 h-8 rounded border border-border bg-white hover:bg-surface hover:border-accent hover:text-accent disabled:opacity-40 disabled:pointer-events-none text-text-secondary transition-all text-xs"
            title="Last page"
          >
            <ChevronsRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </nav>
  );
};
