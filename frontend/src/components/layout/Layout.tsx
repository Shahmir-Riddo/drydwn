import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';
import { BottomNav } from './BottomNav';
import { CustomCursor } from '../common/CustomCursor';
import { SearchModal } from '../common/SearchModal';
import { ScentLogModal } from '../diary/ScentLogModal';

export const Layout: React.FC = () => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [logModalOpen, setLogModalOpen] = useState(false);

  // Global hotkey: Command/Ctrl + K opens search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-bg text-espresso selection:bg-accent/15 selection:text-espresso">
      <CustomCursor />

      <Header
        onOpenSearch={() => setSearchOpen(true)}
        onOpenLogModal={() => setLogModalOpen(true)}
      />

      <main className="flex-1 pb-20 md:pb-0">
        <Outlet context={{ openLogModal: () => setLogModalOpen(true) }} />
      </main>

      <Footer />

      <BottomNav onOpenLogModal={() => setLogModalOpen(true)} />

      <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <ScentLogModal isOpen={logModalOpen} onClose={() => setLogModalOpen(false)} />
    </div>
  );
};
