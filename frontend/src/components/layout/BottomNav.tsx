import React from 'react';
import { NavLink } from 'react-router-dom';
import { BookOpen, Sparkles, Plus, Layers, Send, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { clsx } from 'clsx';

export interface BottomNavProps {
  onOpenLogModal: () => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ onOpenLogModal }) => {
  const { user, isAuthenticated } = useAuth();

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    clsx(
      'flex flex-col items-center justify-center gap-1 flex-1 py-2 px-1 text-[10px] font-label uppercase tracking-wider transition-all duration-200 select-none relative',
      isActive
        ? 'text-accent font-semibold scale-105'
        : 'text-text-secondary/80 hover:text-text-primary'
    );

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-border/70 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] pb-[env(safe-area-inset-bottom)]">
      <div className="flex items-center justify-around h-14 max-w-lg mx-auto px-2">
        {/* Catalogue */}
        <NavLink to="/" end className={navItemClass}>
          {({ isActive }) => (
            <>
              <BookOpen className={clsx('w-4 h-4', isActive ? 'stroke-[2.2]' : 'stroke-[1.6]')} />
              <span className="text-[9px] tracking-widest">Vault</span>
            </>
          )}
        </NavLink>

        {/* Diary */}
        <NavLink to="/diary" className={navItemClass}>
          {({ isActive }) => (
            <>
              <Sparkles className={clsx('w-4 h-4', isActive ? 'stroke-[2.2]' : 'stroke-[1.6]')} />
              <span className="text-[9px] tracking-widest">Diary</span>
            </>
          )}
        </NavLink>

        {/* Center Quick Action: Log Scent */}
        <div className="flex-1 flex justify-center -mt-5">
          <button
            type="button"
            onClick={onOpenLogModal}
            className="w-12 h-12 rounded-full bg-accent text-white flex items-center justify-center shadow-lg shadow-accent/25 border-2 border-white hover:bg-accent-hover active:scale-95 transition-all duration-200"
            aria-label="Log Wear Session"
            title="Log Scent"
          >
            <Plus className="w-6 h-6 stroke-[2.2]" />
          </button>
        </div>

        {/* Wardrobe */}
        <NavLink to="/wardrobe" className={navItemClass}>
          {({ isActive }) => (
            <>
              <Layers className={clsx('w-4 h-4', isActive ? 'stroke-[2.2]' : 'stroke-[1.6]')} />
              <span className="text-[9px] tracking-widest">Wardrobe</span>
            </>
          )}
        </NavLink>

        {/* Request or Profile */}
        {isAuthenticated ? (
          <NavLink to={`/profile/${user?.username}`} className={navItemClass}>
            {({ isActive }) => (
              <>
                <UserIcon className={clsx('w-4 h-4', isActive ? 'stroke-[2.2]' : 'stroke-[1.6]')} />
                <span className="text-[9px] tracking-widest">Dossier</span>
              </>
            )}
          </NavLink>
        ) : (
          <NavLink to="/request" className={navItemClass}>
            {({ isActive }) => (
              <>
                <Send className={clsx('w-4 h-4', isActive ? 'stroke-[2.2]' : 'stroke-[1.6]')} />
                <span className="text-[9px] tracking-widest">Request</span>
              </>
            )}
          </NavLink>
        )}
      </div>
    </div>
  );
};
