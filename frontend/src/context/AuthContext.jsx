import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import client from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing token/user on load
        const token = localStorage.getItem('access_token');
        const userData = localStorage.getItem('user_data');
        const role = localStorage.getItem('role');
        if (token && userData) {
            const parsedUser = JSON.parse(userData);
            // Override with manual role if it exists
            if (role) parsedUser.role = role;
            setUser(parsedUser);
        }
        setLoading(false);
    }, []);

    const fetchUser = async () => {
        try {
            const response = await client.get('/users/me');
            const updatedUser = response.data;

            // Allow manual 'admin' override to persist for testing
            const localRole = localStorage.getItem('role');
            if (localRole === 'admin') {
                updatedUser.role = 'admin';
            } else {
                localStorage.setItem('role', updatedUser.role);
            }

            setUser(updatedUser);
        } catch (error) {
            console.error('Failed to fetch user:', error);
            // If fetching user fails (e.g., token invalid), logout
            logout();
        }
    };

    const login = async (email, password) => {
        try {
            const response = await client.post('/login', { email, password });
            const { access_token } = response.data;

            // Store token
            localStorage.setItem('access_token', access_token);

            // Decode token to get user info immediately
            try {
                const decoded = jwtDecode(access_token);
                const userPayload = {
                    email: decoded.sub,
                    id: decoded.id,
                    role: decoded.role
                };
                setUser(userPayload);
                localStorage.setItem('user_data', JSON.stringify(userPayload));
                localStorage.setItem('role', decoded.role);
            } catch (decodeError) {
                console.error("Token decode failed:", decodeError);
            }

            // Still fetch full profile to ensure we have everything latest
            fetchUser();

            return { success: true };
        } catch (error) {
            console.error('Login failed:', error);
            const errorMsg = error.response?.data?.detail;
            return {
                success: false,
                error: typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg) || 'Login failed'
            };
        }
    };

    const register = async (formData) => {
        try {
            const response = await client.post('/register', formData);
            // Auto login after register
            const { access_token } = response.data;

            localStorage.setItem('access_token', access_token);

            // Decode token to get user info immediately
            try {
                const decoded = jwtDecode(access_token);
                const userPayload = {
                    email: decoded.sub,
                    id: decoded.id,
                    role: decoded.role
                };
                setUser(userPayload);
                localStorage.setItem('user_data', JSON.stringify(userPayload));
                localStorage.setItem('role', decoded.role);
            } catch (decodeError) {
                console.error("Token decode failed:", decodeError);
            }

            // Still fetch full profile to ensure we have everything latest
            fetchUser();

            return { success: true };
        } catch (error) {
            console.error('Registration failed:', error);
            const errorMsg = error.response?.data?.detail;
            return {
                success: false,
                error: typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg) || 'Registration failed'
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('role');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
