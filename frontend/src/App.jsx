import { lazy, Suspense, useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { OrganizationProvider } from './context/OrganizationContext';
import { Spinner } from './components/ui';
import { startOfflineSync } from './lib/offline/sync';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { NotFoundPage } from './pages/NotFoundPage';

const VerifyEmailPage = lazy(() =>
  import('./pages/VerifyEmailPage').then((m) => ({ default: m.VerifyEmailPage })),
);
const ForgotPasswordPage = lazy(() =>
  import('./pages/ForgotPasswordPage').then((m) => ({ default: m.ForgotPasswordPage })),
);
const ResetPasswordPage = lazy(() =>
  import('./pages/ResetPasswordPage').then((m) => ({ default: m.ResetPasswordPage })),
);
const ArticlesPage = lazy(() =>
  import('./pages/ArticlesPage').then((m) => ({ default: m.ArticlesPage })),
);
const ArticleDetailPage = lazy(() =>
  import('./pages/ArticleDetailPage').then((m) => ({ default: m.ArticleDetailPage })),
);
const QuizzesPage = lazy(() =>
  import('./pages/QuizzesPage').then((m) => ({ default: m.QuizzesPage })),
);
const QuizTakePage = lazy(() =>
  import('./pages/QuizTakePage').then((m) => ({ default: m.QuizTakePage })),
);
const ResultsPage = lazy(() =>
  import('./pages/ResultsPage').then((m) => ({ default: m.ResultsPage })),
);
const CertificatesPage = lazy(() =>
  import('./pages/CertificatesPage').then((m) => ({ default: m.CertificatesPage })),
);
const ForumPage = lazy(() =>
  import('./pages/ForumPage').then((m) => ({ default: m.ForumPage })),
);
const TopicDetailPage = lazy(() =>
  import('./pages/TopicDetailPage').then((m) => ({ default: m.TopicDetailPage })),
);
const ProfilePage = lazy(() =>
  import('./pages/ProfilePage').then((m) => ({ default: m.ProfilePage })),
);
const NotificationsPage = lazy(() =>
  import('./pages/NotificationsPage').then((m) => ({ default: m.NotificationsPage })),
);
const AdminPage = lazy(() =>
  import('./pages/AdminPage').then((m) => ({ default: m.AdminPage })),
);
const BillingPage = lazy(() =>
  import('./pages/BillingPage').then((m) => ({ default: m.BillingPage })),
);
const OrganizationPage = lazy(() =>
  import('./pages/OrganizationPage').then((m) => ({ default: m.OrganizationPage })),
);
const DashboardPage = lazy(() =>
  import('./pages/DashboardPage').then((m) => ({ default: m.DashboardPage })),
);
const TutorPage = lazy(() =>
  import('./pages/TutorPage').then((m) => ({ default: m.TutorPage })),
);
const AcceptInvitePage = lazy(() =>
  import('./pages/AcceptInvitePage').then((m) => ({ default: m.AcceptInvitePage })),
);
const SsoCallbackPage = lazy(() =>
  import('./pages/SsoCallbackPage').then((m) => ({ default: m.SsoCallbackPage })),
);
const ArticlesManagePage = lazy(() =>
  import('./pages/ArticlesManagePage').then((m) => ({ default: m.ArticlesManagePage })),
);
const ArticleEditorPage = lazy(() =>
  import('./pages/ArticleEditorPage').then((m) => ({ default: m.ArticleEditorPage })),
);
const QuizzesManagePage = lazy(() =>
  import('./pages/QuizzesManagePage').then((m) => ({ default: m.QuizzesManagePage })),
);
const QuizEditorPage = lazy(() =>
  import('./pages/QuizEditorPage').then((m) => ({ default: m.QuizEditorPage })),
);
const CategoriesManagePage = lazy(() =>
  import('./pages/CategoriesManagePage').then((m) => ({ default: m.CategoriesManagePage })),
);
const MediaPage = lazy(() =>
  import('./pages/MediaPage').then((m) => ({ default: m.MediaPage })),
);
const MediaDetailPage = lazy(() =>
  import('./pages/MediaDetailPage').then((m) => ({ default: m.MediaDetailPage })),
);
const MediaManagePage = lazy(() =>
  import('./pages/MediaManagePage').then((m) => ({ default: m.MediaManagePage })),
);
const MediaEditorPage = lazy(() =>
  import('./pages/MediaEditorPage').then((m) => ({ default: m.MediaEditorPage })),
);
const PrivacyPage = lazy(() =>
  import('./pages/LegalPage').then((m) => ({ default: m.PrivacyPage })),
);
const TermsPage = lazy(() =>
  import('./pages/LegalPage').then((m) => ({ default: m.TermsPage })),
);
const ContactPage = lazy(() =>
  import('./pages/LegalPage').then((m) => ({ default: m.ContactPage })),
);
const SearchPage = lazy(() =>
  import('./pages/SearchPage').then((m) => ({ default: m.SearchPage })),
);
const EngagementPage = lazy(() =>
  import('./pages/EngagementPage').then((m) => ({ default: m.EngagementPage })),
);

function Lazy({ children }) {
  return <Suspense fallback={<Spinner />}>{children}</Suspense>;
}

function guard(element, props = {}) {
  return (
    <ProtectedRoute {...props}>
      <Lazy>{element}</Lazy>
    </ProtectedRoute>
  );
}

export default function App() {
  useEffect(() => startOfflineSync(), []);

  return (
    <ErrorBoundary>
      <AuthProvider>
        <OrganizationProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
                <Route
                  path="invite/:token"
                  element={
                    <Lazy>
                      <AcceptInvitePage />
                    </Lazy>
                  }
                />
                <Route
                  path="verify-email/:token"
                  element={
                    <Lazy>
                      <VerifyEmailPage />
                    </Lazy>
                  }
                />
                <Route
                  path="forgot-password"
                  element={
                    <Lazy>
                      <ForgotPasswordPage />
                    </Lazy>
                  }
                />
                <Route
                  path="reset-password"
                  element={
                    <Lazy>
                      <ResetPasswordPage />
                    </Lazy>
                  }
                />
                <Route
                  path="sso/callback"
                  element={
                    <Lazy>
                      <SsoCallbackPage />
                    </Lazy>
                  }
                />
                <Route
                  path="privacy"
                  element={
                    <Lazy>
                      <PrivacyPage />
                    </Lazy>
                  }
                />
                <Route
                  path="terms"
                  element={
                    <Lazy>
                      <TermsPage />
                    </Lazy>
                  }
                />
                <Route
                  path="contact"
                  element={
                    <Lazy>
                      <ContactPage />
                    </Lazy>
                  }
                />

                <Route
                  path="articles"
                  element={
                    <Lazy>
                      <ArticlesPage />
                    </Lazy>
                  }
                />
                <Route
                  path="articles/manage"
                  element={guard(<ArticlesManagePage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="articles/new"
                  element={guard(<ArticleEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="articles/:id/edit"
                  element={guard(<ArticleEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="articles/:id"
                  element={
                    <Lazy>
                      <ArticleDetailPage />
                    </Lazy>
                  }
                />

                <Route
                  path="search"
                  element={
                    <Lazy>
                      <SearchPage />
                    </Lazy>
                  }
                />

                <Route
                  path="media"
                  element={
                    <Lazy>
                      <MediaPage />
                    </Lazy>
                  }
                />
                <Route
                  path="media/manage"
                  element={guard(<MediaManagePage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="media/new"
                  element={guard(<MediaEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="media/:id/edit"
                  element={guard(<MediaEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="media/:id"
                  element={
                    <Lazy>
                      <MediaDetailPage />
                    </Lazy>
                  }
                />

                <Route
                  path="forum"
                  element={
                    <Lazy>
                      <ForumPage />
                    </Lazy>
                  }
                />
                <Route
                  path="forum/:id"
                  element={
                    <Lazy>
                      <TopicDetailPage />
                    </Lazy>
                  }
                />

                <Route path="quizzes" element={guard(<QuizzesPage />)} />
                <Route
                  path="quizzes/manage"
                  element={guard(<QuizzesManagePage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="quizzes/new"
                  element={guard(<QuizEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route
                  path="quizzes/:id/edit"
                  element={guard(<QuizEditorPage />, {
                    roles: ['admin', 'editor'],
                    orgRoles: ['owner', 'admin', 'content_manager'],
                  })}
                />
                <Route path="quizzes/results" element={guard(<ResultsPage />)} />
                <Route path="quizzes/certificates" element={guard(<CertificatesPage />)} />
                <Route path="quizzes/:id" element={guard(<QuizTakePage />)} />

                <Route path="categories/manage" element={guard(<CategoriesManagePage />)} />
                <Route path="profile" element={guard(<ProfilePage />)} />
                <Route path="notifications" element={guard(<NotificationsPage />)} />
                <Route path="organization" element={guard(<OrganizationPage />)} />
                <Route path="tutor" element={guard(<TutorPage />)} />
                <Route path="engage" element={guard(<EngagementPage />)} />
                <Route path="dashboard" element={guard(<DashboardPage />)} />
                <Route path="billing" element={guard(<BillingPage />)} />
                <Route
                  path="admin"
                  element={guard(<AdminPage />, {
                    roles: ['admin', 'moderator'],
                    orgRoles: ['owner', 'admin', 'moderator'],
                  })}
                />

                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </OrganizationProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
