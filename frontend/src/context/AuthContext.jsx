import React, { createContext, useState, useEffect, useContext } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

const toAuthUser = (apiUser) => ({
    id: apiUser.id,
    email: apiUser.email,
    role: apiUser.role,
    profile: apiUser.profile ?? null,
});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchUser = async () => {
        const response = await client.get('/users/me');
        setUser(toAuthUser(response.data));
        return response.data;
    };

    useEffect(() => {
        const restoreSession = async () => {
            try {
                await fetchUser();
            } catch {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        restoreSession();
    }, []);

    const login = async (email, password) => {
        try {
            await client.post('/login', { email, password });
            await fetchUser();
            return { success: true };
        } catch (error) {
            console.error('Login failed:', error);
            const errorMsg = error.response?.data?.detail;
            return {
                success: false,
                error: typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg) || 'Login failed',
            };
        }
    };

    const register = async (formData) => {
        try {
            await client.post('/register', formData);
            await fetchUser();
            return { success: true };
        } catch (error) {
            console.error('Registration failed:', error);
            const errorMsg = error.response?.data?.detail;
            return {
                success: false,
                error: typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg) || 'Registration failed',
            };
        }
    };

    const logout = async () => {
        try {
            await client.post('/auth/logout');
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
