import React from "react";
import {Navigate, Outlet} from "react-router-dom";
import {useAuth} from "./AuthContext.jsx";
import {Spin} from "antd";

const ProtectedRoute = () => {
    const {user, loading} = useAuth();

    if (loading) return <Spin fullscreen/>;
    return user ? <Outlet/> : <Navigate to="/login" replace/>;
};


export default ProtectedRoute;
