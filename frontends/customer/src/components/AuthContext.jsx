import React, {createContext, useContext, useEffect, useState} from "react";
import api, {setAccessToken} from "../utils/api";

const AuthContext = createContext(null);

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const init = async () => {
            try {
                const res = await api.post("/auth/refresh");
                if (res.data.access_token) {
                    setAccessToken(res.data.access_token);
                    const me = await api.get("/me");
                    setUser(me.data);
                }
            } catch {
                setUser(null);
                setAccessToken(null);
            } finally {
                setLoading(false);
            }
        };
        init();
    }, []);

    const login = async (credentials) => {
        const res = await api.post("/auth/login", credentials, {withCredentials: true});
        if (res.data.access_token) {
            setAccessToken(res.data.access_token);
            const me = await api.get("/me");
            setUser(me.data);
        }
    };

    const logout = async () => {
        try {
            await api.delete("/auth/logout");
        } catch {
        }
        setAccessToken(null);
        setUser(null);
        window.location.href = "/login";
    };

    return (<AuthContext.Provider value={{user, login, logout, loading}}>
        {children}
    </AuthContext.Provider>);
};

export const useAuth = () => useContext(AuthContext);
