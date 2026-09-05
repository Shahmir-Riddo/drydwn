import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  Search,
  Plus,
  User as UserIcon,
  LogOut,
  Settings,
  Sparkles,
  BookOpen,
  Menu,
  X,
  Compass,
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { clsx } from 'clsx';

export interface HeaderProps {
  onOpenSearch: () => void;
  onOpenLogModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSearch, onOpenLogModal }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const navigate = useNavigate();

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    clsx(
      'flex items-center gap-1.5 font-label text-[11px] font-semibold uppercase tracking-[0.2em] transition-colors duration-200 relative py-1',
      isActive
        ? 'text-text-primary after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1.5px] after:bg-accent'
        : 'text-text-secondary hover:text-text-primary after:absolute after:bottom-0 after:left-0 after:w-0 hover:after:w-full after:h-[1.5px] after:bg-accent after:transition-all after:duration-300'
    );

  const handleLogout = () => {
    logout();
    setUserMenuOpen(false);
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 bg-bg/90 backdrop-blur-md border-b border-border/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 gap-4">
          {/* Brand Logo */}
          <Link to="/" className="group flex items-center gap-2.5 shrink-0">
            <span className="font-sans text-xl font-bold tracking-[0.25em] uppercase text-text-primary group-hover:text-accent transition-colors duration-300">
              Drydown
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-7">
            <NavLink to="/" end className={navLinkClass}>
              <BookOpen className="w-3.5 h-3.5 stroke-[1.5]" />
              Catalogue
            </NavLink>
            <NavLink to="/diary" className={navLinkClass}>
              <Sparkles className="w-3.5 h-3.5 stroke-[1.5]" />
              Diary
            </NavLink>
            <NavLink to="/wardrobe" className={navLinkClass}>
              <Layers className="w-3.5 h-3.5 stroke-[1.5]" />
              Wardrobe
            </NavLink>
            <NavLink to="/houses" className={navLinkClass}>
              <Compass className="w-3.5 h-3.5 stroke-[1.5]" />
              Houses
            </NavLink>
          </nav>

          {/* Right Action Icons & User controls */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Quick search button */}
            <button
              onClick={onOpenSearch}
              className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-text-secondary hover:text-text-primary bg-surface hover:bg-surface/80 border border-border/80 rounded-sm transition-colors"
              title="Search fragrances (⌘K)"
            >
              <Search className="w-3.5 h-3.5" />
              <span className="hidden sm:inline font-sans text-[11px] text-text-secondary/70">Search...</span>
              <kbd className="hidden sm:inline text-[9px] font-label uppercase px-1 bg-white border border-border rounded text-text-secondary">
                ⌘K
              </kbd>
            </button>

            {/* Quick Scent Log Trigger */}
            <button
              onClick={onOpenLogModal}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-label uppercase tracking-widest text-white bg-accent hover:bg-accent-hover border border-accent rounded-sm transition-all duration-200 shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Log Scent</span>
            </button>

            {/* Auth Menu */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1 rounded-sm hover:bg-surface transition-colors"
                  aria-label="User menu"
                >
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.display_name || user.username}
                      className="w-7 h-7 rounded-full object-cover border border-sand"
                    />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-surface border border-sand flex items-center justify-center font-label text-[11px] font-semibold text-text-primary">
                      {user?.display_name ? user.display_name.substring(0, 2).toUpperCase() : 'CU'}
                    </div>
                  )}
                </button>

                {/* Dropdown Menu */}
                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white border border-border rounded-sm shadow-lg py-1 z-50 animate-slide-up text-xs font-sans">
                      <div className="px-3 py-2 border-b border-border/50">
                        <p className="font-semibold text-text-primary truncate">
                          {user?.display_name || user?.username}
                        </p>
                        <p className="text-[10px] text-text-secondary truncate">@{user?.username}</p>
                      </div>

                      <Link
                        to={`/profile/${user?.username}`}
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-3 py-2 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
                      >
                        <UserIcon className="w-3.5 h-3.5" />
                        Curator Dossier
                      </Link>
                      <Link
                        to="/feed"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-3 py-2 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        Social Feed
                      </Link>
                      <Link
                        to="/settings"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-3 py-2 text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
                      >
                        <Settings className="w-3.5 h-3.5" />
                        Preferences
                      </Link>

                      <div className="border-t border-border/50 my-1" />

                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 text-rose-600 hover:bg-rose-50/50 transition-colors text-left"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-3 py-1.5 text-xs font-label uppercase tracking-widest text-text-secondary hover:text-text-primary transition-colors"
                >
                  Sign In
                </Link>
              </div>
            )}

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="md:hidden p-1.5 text-text-secondary hover:text-text-primary"
              aria-label="Toggle navigation"
            >
              {mobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile navigation drawer */}
      {mobileNavOpen && (
        <div className="md:hidden border-t border-border/70 bg-bg px-4 pt-3 pb-5 space-y-3">
          <NavLink
            to="/"
            end
            onClick={() => setMobileNavOpen(false)}
            className="flex items-center gap-2.5 py-2 font-label text-xs uppercase tracking-wider text-text-secondary hover:text-text-primary"
          >
            <BookOpen className="w-4 h-4" />
            Catalogue
          </NavLink>
          <NavLink
            to="/diary"
            onClick={() => setMobileNavOpen(false)}
            className="flex items-center gap-2.5 py-2 font-label text-xs uppercase tracking-wider text-text-secondary hover:text-text-primary"
          >
            <Sparkles className="w-4 h-4" />
            Diary
          </NavLink>
          <NavLink
            to="/wardrobe"
            onClick={() => setMobileNavOpen(false)}
            className="flex items-center gap-2.5 py-2 font-label text-xs uppercase tracking-wider text-text-secondary hover:text-text-primary"
          >
            <Layers className="w-4 h-4" />
            Wardrobe
          </NavLink>
          <NavLink
            to="/houses"
            onClick={() => setMobileNavOpen(false)}
            className="flex items-center gap-2.5 py-2 font-label text-xs uppercase tracking-wider text-text-secondary hover:text-text-primary"
          >
            <Compass className="w-4 h-4" />
            Houses
          </NavLink>
          <NavLink
            to="/notes"
            onClick={() => setMobileNavOpen(false)}
            className="flex items-center gap-2.5 py-2 font-label text-xs uppercase tracking-wider text-text-secondary hover:text-text-primary"
          >
            <Sparkles className="w-4 h-4" />
            Notes
          </NavLink>
        </div>
      )}
    </header>
  );
};
