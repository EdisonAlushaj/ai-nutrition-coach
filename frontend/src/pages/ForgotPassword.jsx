import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setIsSubmitting(true);

        try {
            const response = await client.post('/auth/forgot-password', { email });
            setSuccess(response.data.message);
            setEmail('');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map((item) => item.msg).join(' '));
            } else {
                setError(typeof detail === 'string' ? detail : 'Unable to process request.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20">
            <div className="max-w-md w-full bg-brand-surface/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-2">Forgot Password</h2>
                    <p className="text-gray-400">Enter your email and we will send you a reset link.</p>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 px-4 py-3 rounded-lg mb-6 text-sm">
                        {success}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="email">
                            Email Address
                        </label>
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

                    <button
                        className={`w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg shadow-brand-primary/25 ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
                        type="submit"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Sending...' : 'Send Reset Link'}
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

export default ForgotPassword;
