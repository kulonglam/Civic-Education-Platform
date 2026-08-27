import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { Spinner } from './ui';
import { platformRoleAllowed } from '../lib/roles';

/**
 * Gate by platform roles and/or org membership roles (OR logic).
 * Example: roles={['admin','editor']} orgRoles={['owner','admin','content_manager']}
 */
function ProtectedRoute({
  children,
  roles,
  orgRoles,
}: {
  children: ReactNode;
  roles?: string[];
  orgRoles?: string[];
}) {
  const { user, loading } = useAuth();
  const { membership, loading: orgLoading } = useOrganization();
  const location = useLocation();

  if (loading || (user && orgLoading)) return <Spinner />;
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (roles || orgRoles) {
    const platformOk = roles ? platformRoleAllowed(user.role?.name, roles) : false;
    const orgOk = orgRoles && membership?.role ? orgRoles.includes(membership.role) : false;
    if (!platformOk && !orgOk) {
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
}

export { ProtectedRoute };
