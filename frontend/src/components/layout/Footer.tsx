import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-border/80 bg-bg py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-1 text-center md:text-left">
            <span className="font-sans text-base font-bold tracking-[0.2em] uppercase text-text-primary">
              Drydown
            </span>
            <p className="font-sans text-xs text-text-secondary">
              A private vault for olfactory connoisseurs and perfume collectors.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-label uppercase tracking-widest text-text-secondary">
            <Link to="/" className="hover:text-accent transition-colors">
              Catalogue
            </Link>
            <Link to="/houses" className="hover:text-accent transition-colors">
              Houses
            </Link>
            <Link to="/notes" className="hover:text-accent transition-colors">
              Notes
            </Link>
            <Link to="/request-fragrance" className="hover:text-accent transition-colors">
              Request Fragrance
            </Link>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-border/40 flex flex-col sm:flex-row items-center justify-between text-[11px] text-text-secondary/70">
          <p>© {new Date().getFullYear()} DRYDOWN Vault. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 font-label tracking-wider">REST API v1 · React SPA</p>
        </div>
      </div>
    </footer>
  );
};
