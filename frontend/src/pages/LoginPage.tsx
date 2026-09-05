import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import type { LoginPayload } from '../api/auth';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginPayload>();

  const onSubmit = async (data: LoginPayload) => {
    setIsSubmitting(true);
    try {
      await login(data);
      showToast('Welcome back to DRYDOWN', 'success');
      navigate(from, { replace: true });
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        'Unable to log in with provided credentials. Please check your username and password.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 sm:py-24 space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.3em] text-accent">
          Curator Access
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-normal text-text-primary tracking-tight">
          Enter Your Vault
        </h1>
        <p className="font-sans text-xs text-text-secondary">
          Access your personal scent diary, collection shelves, and community votes.
        </p>
      </div>

      <div className="vault-card p-6 sm:p-8 space-y-6">
        {/* Google OAuth Button */}
        <a
          href="/accounts/google/login/"
          className="w-full inline-flex items-center justify-center gap-3 px-4 py-2.5 bg-white border border-border hover:border-accent text-xs font-sans text-text-primary rounded-sm transition-all shadow-xs group"
        >
          <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
            />
            <path
              fill="#34A853"
              d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
            />
            <path
              fill="#EA4335"
              d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
            />
          </svg>
          <span className="font-medium group-hover:text-accent transition-colors">
            Continue with Google
          </span>
        </a>

        <div className="relative flex items-center justify-center">
          <div className="border-t border-border/80 w-full" />
          <span className="bg-white px-3 text-[10px] font-label uppercase tracking-widest text-text-secondary/70 absolute">
            Or With Credentials
          </span>
        </div>

        {/* Credentials Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Username"
            placeholder="curator_handle"
            {...register('username', { required: 'Username is required' })}
            error={errors.username?.message}
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            {...register('password', { required: 'Password is required' })}
            error={errors.password?.message}
          />

          <Button type="submit" variant="accent" size="lg" className="w-full" isLoading={isSubmitting}>
            Sign In to Vault
          </Button>
        </form>

        <div className="pt-2 text-center text-xs text-text-secondary space-y-2">
          <p>
            <a href="/accounts/password-reset/" className="text-text-muted hover:text-accent transition-colors">
              Forgot your password?
            </a>
          </p>
          <p>
            Don't have a curator vault yet?{' '}
            <Link to="/register" className="text-accent hover:underline font-medium">
              Create Account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
