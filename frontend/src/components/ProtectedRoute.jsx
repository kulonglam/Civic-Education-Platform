import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "./ui";
function ProtectedRoute({
  children,
  roles
}) {
  const {
    user,
    loading
  } = useAuth();
  const location = useLocation();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" state={{
    from: location.pathname
  }} replace />;
  if (roles && !roles.includes(user.role.name)) return <Navigate to="/" replace />;
  return <>{children}</>;
}
export { ProtectedRoute };