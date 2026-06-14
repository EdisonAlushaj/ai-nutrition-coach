import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const resetSuccess = searchParams.get('reset') === 'success';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        const result = await login(email, password);
        setIsSubmitting(false);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error || 'Login failed');
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20">
            <div className="max-w-md w-full bg-brand-surface/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
                    <p className="text-gray-400">Enter your details to access your account</p>
                </div>

                {resetSuccess && (
                    <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 px-4 py-3 rounded-lg mb-6 text-sm">
                        Password updated successfully. You can sign in with your new password.
                    </div>
                )}

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="email">Email Address</label>
                        <input
                            className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                            id="email"
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="block text-gray-300 text-sm font-medium" htmlFor="password">Password</label>
                            <Link to="/forgot-password" className="text-sm text-brand-primary hover:text-brand-accent transition-colors">
                                Forgot?
                            </Link>
                        </div>
                        <input
                            className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                            id="password"
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        className={`w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg shadow-brand-primary/25 ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
                        type="submit"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Logging in...' : 'Sign In'}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <p className="text-gray-400">
                        New here?{' '}
                        <Link to="/register" className="text-brand-primary font-bold hover:text-white transition-colors">
                            Create an account
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
