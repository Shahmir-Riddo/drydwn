import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Compass } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="max-w-md mx-auto py-24 px-4 text-center space-y-5 animate-fade-in">
      <Compass className="w-12 h-12 text-accent/50 mx-auto" />
      <span className="text-[11px] font-label font-semibold uppercase tracking-[0.3em] text-accent">
        404 — Page Not Found
      </span>
      <h1 className="font-serif text-4xl font-normal text-text-primary">
        An Uncharted Note
      </h1>
      <p className="font-sans text-xs text-text-secondary leading-relaxed">
        The corridor or flacon you are seeking does not exist in the Drydown archive.
      </p>
      <div className="pt-2">
        <Link to="/">
          <Button variant="accent">Return to Catalogue</Button>
        </Link>
      </div>
    </div>
  );
};
