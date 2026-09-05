import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'md',
}) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 overflow-y-auto">
      {/* Backdrop blur */}
      <div
        className="fixed inset-0 bg-espresso/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal dialog / Mobile bottom sheet */}
      <div
        className={clsx(
          'relative w-full bg-white border-t sm:border border-border rounded-t-2xl sm:rounded-sm shadow-2xl z-10 max-h-[92vh] sm:max-h-[88vh] flex flex-col overflow-hidden animate-slide-up',
          maxWidthClasses[maxWidth]
        )}
      >
        {/* Mobile drag handle bar */}
        <div className="sm:hidden flex justify-center pt-2.5 pb-1">
          <div className="w-10 h-1 rounded-full bg-border" />
        </div>

        {(title || subtitle) && (
          <div className="px-5 sm:px-6 py-3.5 sm:py-4 border-b border-border/60 flex items-start justify-between shrink-0">
            <div>
              {title && <h3 className="font-serif text-lg sm:text-xl font-normal text-text-primary">{title}</h3>}
              {subtitle && <p className="font-sans text-[11px] sm:text-xs text-text-secondary mt-0.5">{subtitle}</p>}
            </div>
            <button
              onClick={onClose}
              className="text-text-secondary hover:text-text-primary transition-colors p-1.5 -mr-2 rounded-full hover:bg-surface"
              aria-label="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        <div className="p-4 sm:p-6 overflow-y-auto overscroll-contain flex-1">{children}</div>
      </div>
    </div>
  );
};
