import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { Layout } from './components/layout/Layout';
import { Skeleton } from './components/common/Skeleton';

// Code-split route definitions for minimal initial JS bundle payload
const HomePage = lazy(() => import('./pages/HomePage').then((m) => ({ default: m.HomePage })));
const FragranceDetailPage = lazy(() =>
  import('./pages/FragranceDetailPage').then((m) => ({ default: m.FragranceDetailPage }))
);
const DiaryPage = lazy(() => import('./pages/DiaryPage').then((m) => ({ default: m.DiaryPage })));
const DiaryDetailPage = lazy(() =>
  import('./pages/DiaryDetailPage').then((m) => ({ default: m.DiaryDetailPage }))
);
const WardrobePage = lazy(() => import('./pages/WardrobePage').then((m) => ({ default: m.WardrobePage })));
const HousesPage = lazy(() => import('./pages/HousesPage').then((m) => ({ default: m.HousesPage })));
const HouseDetailPage = lazy(() =>
  import('./pages/HouseDetailPage').then((m) => ({ default: m.HouseDetailPage }))
);
const NotesPage = lazy(() => import('./pages/NotesPage').then((m) => ({ default: m.NotesPage })));
const NoteDetailPage = lazy(() =>
  import('./pages/NoteDetailPage').then((m) => ({ default: m.NoteDetailPage }))
);
const LoginPage = lazy(() => import('./pages/LoginPage').then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('./pages/RegisterPage').then((m) => ({ default: m.RegisterPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then((m) => ({ default: m.ProfilePage })));
const EditProfilePage = lazy(() =>
  import('./pages/EditProfilePage').then((m) => ({ default: m.EditProfilePage }))
);
const SettingsPage = lazy(() => import('./pages/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const FeedPage = lazy(() => import('./pages/FeedPage').then((m) => ({ default: m.FeedPage })));
const NetworkPage = lazy(() => import('./pages/NetworkPage').then((m) => ({ default: m.NetworkPage })));
const FragranceRequestPage = lazy(() =>
  import('./pages/FragranceRequestPage').then((m) => ({ default: m.FragranceRequestPage }))
);
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage })));

// TanStack Query client with caching defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Route Guard for authenticated curators
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return <PageLoadingSkeleton />;
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

// Subtle full-screen loading skeleton for lazy-loaded route chunk transitions
const PageLoadingSkeleton: React.FC = () => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6 animate-fade-in">
    <Skeleton className="h-10 w-48" />
    <Skeleton className="h-4 w-72" />
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
      {Array.from({ length: 8 }).map((_, i) => (
        <Skeleton key={i} className="aspect-[3/4]" />
      ))}
    </div>
  </div>
);

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Suspense fallback={<PageLoadingSkeleton />}>
              <Routes>
                <Route element={<Layout />}>
                  {/* Public Core Routes */}
                  <Route path="/" element={<HomePage />} />
                  <Route path="/fragrance/:id" element={<FragranceDetailPage />} />
                  <Route path="/houses" element={<HousesPage />} />
                  <Route path="/houses/:id" element={<HouseDetailPage />} />
                  <Route path="/notes" element={<NotesPage />} />
                  <Route path="/notes/:id" element={<NoteDetailPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/profile/:username" element={<ProfilePage />} />
                  <Route path="/profile/:username/followers" element={<NetworkPage />} />
                  <Route path="/profile/:username/following" element={<NetworkPage />} />

                  {/* Authenticated Routes */}
                  <Route
                    path="/diary"
                    element={
                      <ProtectedRoute>
                        <DiaryPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/diary/:id"
                    element={
                      <ProtectedRoute>
                        <DiaryDetailPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/wardrobe"
                    element={
                      <ProtectedRoute>
                        <WardrobePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile/edit"
                    element={
                      <ProtectedRoute>
                        <EditProfilePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <SettingsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/feed"
                    element={
                      <ProtectedRoute>
                        <FeedPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/request-fragrance"
                    element={
                      <ProtectedRoute>
                        <FragranceRequestPage />
                      </ProtectedRoute>
                    }
                  />

                  {/* 404 Fallback */}
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};
