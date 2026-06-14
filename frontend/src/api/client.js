import axios from 'axios';

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

let refreshPromise = null;

client.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        const isAuthRoute = originalRequest?.url?.includes('/auth/refresh')
            || originalRequest?.url?.includes('/login')
            || originalRequest?.url?.includes('/register');

        if (
            error.response?.status === 401
            && originalRequest
            && !originalRequest._retry
            && !isAuthRoute
        ) {
            originalRequest._retry = true;

            if (!refreshPromise) {
                refreshPromise = client.post('/auth/refresh').finally(() => {
                    refreshPromise = null;
                });
            }

            try {
                await refreshPromise;
                return client(originalRequest);
            } catch (refreshError) {
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    },
);

export default client;
