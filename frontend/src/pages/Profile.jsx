import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';
const Profile = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [mealPlan, setMealPlan] = useState([]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    useEffect(() => {
        if (user) {
            fetchProfile();
            fetchMealPlan();
        }
    }, [user]);

    const fetchProfile = async () => {
        try {
            const response = await client.get('/users/me');
            setProfile(response.data.profile);
        } catch (error) {
            console.error('Failed to fetch profile:', error);
        }
    };

    const fetchMealPlan = async () => {
        try {
            const response = await client.get(`/users/${user.id}/meal-plan`);
            setMealPlan(response.data);
        } catch (error) {
            console.error('Failed to fetch meal plan:', error);
        }
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 md:px-8 max-w-2xl mx-auto">

            {/* Navigation Back */}
            <Link
                to="/dashboard"
                className="inline-flex items-center text-gray-400 hover:text-brand-primary transition-colors mb-8 group"
            >
                <span className="mr-2 group-hover:-translate-x-1 transition-transform">←</span>
                Back to Dashboard
            </Link>

            {/* Profile Header */}
            <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-8 mb-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-brand-primary/10 rounded-full blur-[40px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="flex flex-col items-center text-center">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center text-3xl font-bold mb-4 shadow-xl shadow-brand-primary/20">
                        {user?.name?.[0] || 'U'}
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">{user?.name || 'Athlete'}</h1>
                    <p className="text-gray-400">{user?.email}</p>
                    <div className="mt-4 px-3 py-1 bg-white/5 rounded-full text-xs text-brand-primary border border-brand-primary/20 uppercase tracking-widest font-bold">
                        User ID: {user?.id}
                    </div>
                </div>
            </div>

            {/* Profile Sections */}
            <div className="space-y-6">

                {/* Information Card */}
                <div className="bg-brand-surface/30 border border-white/5 rounded-2xl p-6">
                    <h2 className="text-lg font-bold text-white mb-4">Account Information</h2>
                    <div className="space-y-4">
                        <InfoItem label="Full Name" value={user?.name || 'Not Set'} />
                        <InfoItem label="Email Address" value={user?.email} />
                        <InfoItem label="Account Type" value={user?.role || 'User'} />
                    </div>
                </div>

                {/* Goals Card */}
                <div className="bg-brand-surface/30 border border-white/5 rounded-2xl p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-white">Fitness Profile</h2>
                    </div>
                    <div className="space-y-4">
                        <InfoItem
                            label="Current Goal"
                            value={profile?.goal ? profile.goal.replace(/_/g, ' ').toUpperCase() : 'Not Set'}
                        />
                        <InfoItem
                            label="Activity Level"
                            value={profile?.activity_level ? profile.activity_level.replace(/_/g, ' ').toUpperCase() : 'Not Set'}
                        />
                        <div className="grid grid-cols-2 gap-4 pt-2">
                            <InfoItem label="Height" value={profile?.height_cm ? `${profile.height_cm} cm` : '-'} />
                            <InfoItem label="Weight" value={profile?.weight_kg ? `${profile.weight_kg} kg` : '-'} />
                        </div>
                    </div>
                </div>

                {/* Meal Plan Section */}
                {mealPlan.length > 0 && (
                    <div className="bg-brand-surface/30 border border-white/5 rounded-2xl p-6">
                        <h2 className="text-lg font-bold text-white mb-4">Recommended Meal Plan</h2>
                        <div className="space-y-4">
                            {mealPlan.map((meal) => (
                                <div key={meal.id} className="bg-white/5 rounded-xl p-4 border border-white/5">
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="font-bold text-white">{meal.name}</h3>
                                        <span className="text-brand-primary text-sm font-bold">{meal.total_calories} kcal</span>
                                    </div>
                                    <p className="text-sm text-gray-400 mb-3">{meal.description}</p>
                                    <div className="grid grid-cols-3 gap-2 text-xs">
                                        <div className="bg-brand-dark/50 rounded p-2 text-center">
                                            <span className="block text-gray-400">Protein</span>
                                            <span className="text-white font-bold">{meal.protein_g}g</span>
                                        </div>
                                        <div className="bg-brand-dark/50 rounded p-2 text-center">
                                            <span className="block text-gray-400">Carbs</span>
                                            <span className="text-white font-bold">{meal.carbs_g}g</span>
                                        </div>
                                        <div className="bg-brand-dark/50 rounded p-2 text-center">
                                            <span className="block text-gray-400">Fat</span>
                                            <span className="text-white font-bold">{meal.fat_g}g</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Dangerous Actions */}
                <div className="pt-4">
                    <button
                        onClick={handleLogout}
                        className="w-full bg-red-500/10 border border-red-500/20 text-red-500 py-4 rounded-2xl font-bold hover:bg-red-500 hover:text-white transition-all shadow-lg hover:shadow-red-500/20 active:scale-[0.98]"
                    >
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
    );
};

const InfoItem = ({ label, value }) => (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
        <span className="text-gray-400 text-sm">{label}</span>
        <span className="text-white font-medium">{value}</span>
    </div>
);

export default Profile;
