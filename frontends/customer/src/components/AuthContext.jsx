import React, {createContext, useContext, useEffect, useState} from "react";
import api, {setAccessToken} from "../utils/api.js";

const AuthContext = createContext(null);

export const AuthProvider = ({children}) => {
    const [accessToken, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {

            const rememberedToken = localStorage.getItem("access_token");
            if (rememberedToken) {
                setToken(rememberedToken);
                setAccessToken(rememberedToken);
                setLoading(false);
                return;
            }

            try {
                const res = await api.post("/auth/refresh", {}, {withCredentials: true});
                setToken(res.data.access_token);
                setAccessToken(res.data.access_token);
            } catch (error) {
                setToken(null);
            } finally {
                setLoading(false);
            }
        };
        initAuth();
    }, []);


    const login = (token, remember = false) => {
        setToken(token);
        setAccessToken(token);

        if (remember) {
            localStorage.setItem("access_token", token);
        } else {
            localStorage.removeItem("access_token");
        }
    };

    const logout = async () => {
        try {
            await api.delete("/auth/logout");
        } catch {
        }
        setToken(null);
        setAccessToken(null);
        localStorage.removeItem("access_token");
    };

    return (
        <AuthContext.Provider value={{accessToken, login, logout, loading}}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
