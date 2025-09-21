import React from "react";
import {Navigate, Outlet} from "react-router-dom";
import {Spin} from "antd";
import {useAuth} from "./AuthContext.jsx";
import {hasAccess} from "../utils/rbac";

const ProtectedRoute = ({roles}) => {
    const {user, loading} = useAuth();

    if (loading) return <Spin fullscreen/>;
    if (!user) return <Navigate to="/login" replace/>;

    if (roles && !hasAccess(user.role, roles)) {
        return <Navigate to="/" replace/>;
    }

    return <Outlet/>;
};

export default ProtectedRoute;
