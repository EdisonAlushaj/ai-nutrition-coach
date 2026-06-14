import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import client from '../api/client';

const ResetPassword = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get('token') || '';

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [tokenError, setTokenError] = useState('');
    const [isValidating, setIsValidating] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        const validateToken = async () => {
            if (!token) {
                setTokenError('Reset link is missing or invalid.');
                setIsValidating(false);
                return;
            }

            try {
                await client.get('/auth/reset-password/validate', { params: { token } });
                setTokenError('');
            } catch {
                setTokenError('This reset link is invalid or has expired.');
            } finally {
                setIsValidating(false);
            }
        };

        validateToken();
    }, [token]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (newPassword !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        setIsSubmitting(true);
        try {
            await client.post('/auth/reset-password', {
                token,
                new_password: newPassword,
                confirm_password: confirmPassword,
            });
            navigate('/login?reset=success');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map((item) => item.msg).join(' '));
            } else {
                setError(typeof detail === 'string' ? detail : 'Unable to reset password.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isValidating) {
        return (
            <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
            </div>
        );
    }

    if (tokenError) {
        return (
            <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20">
                <div className="max-w-md w-full bg-brand-surface/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl text-center">
                    <h2 className="text-2xl font-bold text-white mb-4">Reset Link Invalid</h2>
                    <p className="text-gray-400 mb-8">{tokenError}</p>
                    <Link
                        to="/forgot-password"
                        className="text-brand-primary font-bold hover:text-white transition-colors"
                    >
                        Request a new reset link
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20">
            <div className="max-w-md w-full bg-brand-surface/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-2">Set New Password</h2>
                    <p className="text-gray-400">Choose a strong password with at least 8 characters.</p>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="newPassword">
                            New Password
                        </label>
                        <input
                            className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                            id="newPassword"
                            type="password"
                            placeholder="At least 8 characters"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            minLength={8}
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="confirmPassword">
                            Confirm Password
                        </label>
                        <input
                            className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                            id="confirmPassword"
                            type="password"
                            placeholder="Repeat your password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            minLength={8}
                            required
                        />
                    </div>

                    <button
                        className={`w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg shadow-brand-primary/25 ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
                        type="submit"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Updating...' : 'Update Password'}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <Link to="/login" className="text-brand-primary font-bold hover:text-white transition-colors">
                        Back to Sign In
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ResetPassword;
