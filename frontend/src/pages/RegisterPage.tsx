import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import type { RegisterPayload } from '../api/auth';

export const RegisterPage: React.FC = () => {
  const { register: registerUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterPayload>();

  const password = watch('password');

  const onSubmit = async (data: RegisterPayload) => {
    setIsSubmitting(true);
    try {
      await registerUser(data);
      showToast('Welcome to DRYDOWN! Your vault account is ready.', 'success');
      navigate('/', { replace: true });
    } catch (err: any) {
      const msg =
        err.response?.data?.username?.[0] ||
        err.response?.data?.email?.[0] ||
        err.response?.data?.password_confirm?.[0] ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.detail ||
        'Registration failed. Please check the entered fields.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 sm:py-20 space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <span className="text-[11px] font-label font-semibold uppercase tracking-[0.3em] text-accent">
          Membership
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-normal text-text-primary tracking-tight">
          Create Curator Vault
        </h1>
        <p className="font-sans text-xs text-text-secondary">
          Join the olfactory community to log wears, rate notes, and catalog your flacons.
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
            Sign Up with Google
          </span>
        </a>

        <div className="relative flex items-center justify-center">
          <div className="border-t border-border/80 w-full" />
          <span className="bg-white px-3 text-[10px] font-label uppercase tracking-widest text-text-secondary/70 absolute">
            Or Register Below
          </span>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Curator Username *"
            placeholder="e.g. olivier_c"
            {...register('username', {
              required: 'Username is required',
              minLength: { value: 3, message: 'Minimum 3 characters' },
            })}
            error={errors.username?.message}
          />

          <Input
            label="Email Address *"
            type="email"
            placeholder="curator@example.com"
            {...register('email', {
              required: 'Email is required',
              pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' },
            })}
            error={errors.email?.message}
          />

          <Input
            label="Password *"
            type="password"
            placeholder="••••••••"
            {...register('password', {
              required: 'Password is required',
            })}
            error={errors.password?.message}
          />

          <Input
            label="Confirm Password *"
            type="password"
            placeholder="••••••••"
            {...register('password_confirm', {
              required: 'Please confirm password',
              validate: (val) => val === password || 'Passwords do not match',
            })}
            error={errors.password_confirm?.message}
          />

          <Button type="submit" variant="accent" size="lg" className="w-full" isLoading={isSubmitting}>
            Create Vault Account
          </Button>
        </form>

        <div className="pt-2 text-center text-xs text-text-secondary">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="text-accent hover:underline font-medium">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
