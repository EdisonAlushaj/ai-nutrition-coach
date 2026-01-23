import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [step, setStep] = useState(1);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        profile: {
            age: '',
            gender: 'male',
            height_cm: '',
            weight_kg: '',
            activity_level: 'sedentary',
            goal: 'lose_weight'
        }
    });

    const updateFormData = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    }

    const updateProfile = (field, value) => {
        setFormData(prev => ({
            ...prev,
            profile: { ...prev.profile, [field]: value }
        }));
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Basic validation for numbers
        if (formData.profile.age <= 0 || formData.profile.height_cm <= 0 || formData.profile.weight_kg <= 0) {
            setError('Please enter valid positive numbers for age, height, and weight.');
            return;
        }

        const result = await register(formData);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error || 'Registration failed');
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 pt-20 pb-10">
            <div className="max-w-md w-full bg-brand-surface/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-brand-primary to-brand-accent"></div>

                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Join the Movement</h2>
                    <p className="text-gray-400">Step {step} of 2: {step === 1 ? 'Account Details' : 'Your Profile'}</p>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={step === 1 ? (e) => { e.preventDefault(); setStep(2); } : handleSubmit} className="space-y-5">

                    {step === 1 && (
                        <>
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2">Email Address</label>
                                <input
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                                    type="email"
                                    required
                                    placeholder="you@example.com"
                                    value={formData.email}
                                    onChange={(e) => updateFormData('email', e.target.value)}
                                />
                            </div>
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2">Password</label>
                                <input
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                                    type="password"
                                    required
                                    placeholder="Create a strong password"
                                    value={formData.password}
                                    onChange={(e) => updateFormData('password', e.target.value)}
                                />
                            </div>
                            <button
                                type="submit"
                                className="w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all duration-300 mt-2"
                            >
                                Next Step
                            </button>
                        </>
                    )}

                    {step === 2 && (
                        <>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-300 text-sm font-medium mb-2">Age</label>
                                    <input
                                        className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                        type="number"
                                        required
                                        value={formData.profile.age}
                                        onChange={(e) => updateProfile('age', e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-300 text-sm font-medium mb-2">Gender</label>
                                    <select
                                        className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                        value={formData.profile.gender}
                                        onChange={(e) => updateProfile('gender', e.target.value)}
                                    >
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-300 text-sm font-medium mb-2">Height (cm)</label>
                                    <input
                                        className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                        type="number"
                                        required
                                        value={formData.profile.height_cm}
                                        onChange={(e) => updateProfile('height_cm', e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-300 text-sm font-medium mb-2">Weight (kg)</label>
                                    <input
                                        className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                        type="number"
                                        required
                                        value={formData.profile.weight_kg}
                                        onChange={(e) => updateProfile('weight_kg', e.target.value)}
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2">Activity Level</label>
                                <select
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                    value={formData.profile.activity_level}
                                    onChange={(e) => updateProfile('activity_level', e.target.value)}
                                >
                                    <option value="sedentary">Sedentary (Office job)</option>
                                    <option value="lightly_active">Lightly Active (1-3 days/week)</option>
                                    <option value="moderately_active">Moderately Active (3-5 days/week)</option>
                                    <option value="very_active">Very Active (6-7 days/week)</option>
                                    <option value="extra_active">Extra Active (Physically demanding)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2">Goal</label>
                                <select
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary"
                                    value={formData.profile.goal}
                                    onChange={(e) => updateProfile('goal', e.target.value)}
                                >
                                    <option value="lose_weight">Lose Weight</option>
                                    <option value="maintain">Maintain Weight</option>
                                    <option value="gain_muscle">Gain Muscle</option>
                                </select>
                            </div>

                            <div className="flex gap-4 mt-2">
                                <button
                                    type="button"
                                    onClick={() => setStep(1)}
                                    className="w-1/3 border border-white/10 text-white font-bold py-3.5 px-4 rounded-xl hover:bg-white/5 transition-all"
                                >
                                    Back
                                </button>
                                <button
                                    type="submit"
                                    className="w-2/3 bg-gradient-to-r from-brand-primary to-emerald-500 hover:from-emerald-400 hover:to-emerald-400 text-white font-bold py-3.5 px-4 rounded-xl transition-all shadow-lg"
                                >
                                    Create Account
                                </button>
                            </div>
                        </>
                    )}
                </form>

                <div className="mt-8 text-center">
                    <p className="text-gray-400">
                        Already a member?{' '}
                        <Link to="/login" className="text-brand-primary font-bold hover:text-white transition-colors">
                            Log in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register;
