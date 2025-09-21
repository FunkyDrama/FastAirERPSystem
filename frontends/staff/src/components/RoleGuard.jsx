import {useAuth} from "./AuthContext.jsx";
import {hasAccess} from "../utils/rbac";

const RoleGuard = ({roles, children, fallback = null}) => {
    const {user, loading} = useAuth();

    if (loading) return null;
    if (!hasAccess(user?.role, roles)) return fallback;

    return children;
};

export default RoleGuard;