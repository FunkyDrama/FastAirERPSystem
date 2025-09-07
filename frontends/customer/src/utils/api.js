import axios from "axios";

let accessToken = null;
export const setAccessToken = (token) => {
    accessToken = token;
};
export const getAccessToken = () => accessToken;

const api = axios.create({
    baseURL: "/api/v1",
    withCredentials: true,
});


api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});


api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            const isOnLoginPage = window.location.pathname === "/login";

            try {
                if (!isOnLoginPage) {
                    const res = await axios.post(
                        "http://localhost:8001/api/v1/auth/refresh",
                        {},
                        {withCredentials: true}
                    );
                    const newAccess = res.data.access_token;
                    setAccessToken(newAccess);

                    error.config.headers.Authorization = `Bearer ${newAccess}`;
                    return api(error.config);
                }
            } catch (refreshError) {
                if (!isOnLoginPage) {
                    setAccessToken(null);
                }
            }
        }
        return Promise.reject(error);
    }
);


export default api;
