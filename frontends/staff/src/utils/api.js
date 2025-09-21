import axios from "axios";
import createAuthRefreshInterceptor from "axios-auth-refresh";

let accessToken = null;

export const setAccessToken = (token) => {
    accessToken = token;
};
const api = axios.create({
    baseURL: "/api/v1/staff",
    withCredentials: true,
});

api.interceptors.request.use((config) => {
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

const refreshAuthLogic = async (failedRequest) => {
    const res = await api.post("/auth/refresh");
    const newToken = res.data.access_token;
    setAccessToken(newToken);
    failedRequest.response.config.headers.Authorization = `Bearer ${newToken}`;
    return Promise.resolve();
};


createAuthRefreshInterceptor(api, refreshAuthLogic, {
    statusCodes: [401],
    pauseInstanceWhileRefreshing: true,
    skipAuthRefresh: (error) => {
        const url = error?.config?.url || "";
        return url.includes("/auth/login") || url.includes("/auth/refresh") || url.includes("/auth/google");
    }

});


export default api;
