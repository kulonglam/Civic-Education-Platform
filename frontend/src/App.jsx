import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { OrganizationProvider } from './context/OrganizationContext';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { ArticlesPage } from './pages/ArticlesPage';
import { ArticleDetailPage } from './pages/ArticleDetailPage';
import { QuizzesPage } from './pages/QuizzesPage';
import { QuizTakePage } from './pages/QuizTakePage';
import { ResultsPage } from './pages/ResultsPage';
import { CertificatesPage } from './pages/CertificatesPage';
import { ForumPage } from './pages/ForumPage';
import { TopicDetailPage } from './pages/TopicDetailPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotificationsPage } from './pages/NotificationsPage';
import { AdminPage } from './pages/AdminPage';
import { BillingPage } from './pages/BillingPage';
import { OrganizationPage } from './pages/OrganizationPage';
import { DashboardPage } from './pages/DashboardPage';
import { TutorPage } from './pages/TutorPage';
import { AcceptInvitePage } from './pages/AcceptInvitePage';
import { SsoCallbackPage } from './pages/SsoCallbackPage';
import { ArticlesManagePage } from './pages/ArticlesManagePage';
import { ArticleEditorPage } from './pages/ArticleEditorPage';
import { QuizzesManagePage } from './pages/QuizzesManagePage';
import { QuizEditorPage } from './pages/QuizEditorPage';
import { CategoriesManagePage } from './pages/CategoriesManagePage';
import { NotFoundPage } from './pages/NotFoundPage';
import { PrivacyPage, TermsPage } from './pages/LegalPage';

export default function App() {
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
                <Route path="invite/:token" element={<AcceptInvitePage />} />
                <Route path="verify-email/:token" element={<VerifyEmailPage />} />
                <Route path="forgot-password" element={<ForgotPasswordPage />} />
                <Route path="reset-password" element={<ResetPasswordPage />} />
                <Route path="sso/callback" element={<SsoCallbackPage />} />
                <Route path="privacy" element={<PrivacyPage />} />
                <Route path="terms" element={<TermsPage />} />

                <Route path="articles" element={<ArticlesPage />} />
                <Route
                  path="articles/manage"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <ArticlesManagePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="articles/new"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <ArticleEditorPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="articles/:id/edit"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <ArticleEditorPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="articles/:id" element={<ArticleDetailPage />} />

                <Route path="forum" element={<ForumPage />} />
                <Route path="forum/:id" element={<TopicDetailPage />} />

                <Route
                  path="quizzes"
                  element={
                    <ProtectedRoute>
                      <QuizzesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/manage"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <QuizzesManagePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/new"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <QuizEditorPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/:id/edit"
                  element={
                    <ProtectedRoute roles={['admin', 'editor']}>
                      <QuizEditorPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/results"
                  element={
                    <ProtectedRoute>
                      <ResultsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/certificates"
                  element={
                    <ProtectedRoute>
                      <CertificatesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="quizzes/:id"
                  element={
                    <ProtectedRoute>
                      <QuizTakePage />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="categories/manage"
                  element={
                    <ProtectedRoute>
                      <CategoriesManagePage />
                    </ProtectedRoute>
                  }
                />

                <Route
                  path="profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="notifications"
                  element={
                    <ProtectedRoute>
                      <NotificationsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="organization"
                  element={
                    <ProtectedRoute>
                      <OrganizationPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="tutor"
                  element={
                    <ProtectedRoute>
                      <TutorPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="billing"
                  element={
                    <ProtectedRoute>
                      <BillingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="admin"
                  element={
                    <ProtectedRoute roles={['admin', 'moderator']}>
                      <AdminPage />
                    </ProtectedRoute>
                  }
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
