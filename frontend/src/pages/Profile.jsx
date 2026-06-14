import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';

const ACTIVITY_LEVELS = [
    { value: 'sedentary', label: 'Sedentary' },
    { value: 'lightly_active', label: 'Lightly active' },
    { value: 'moderately_active', label: 'Moderately active' },
    { value: 'very_active', label: 'Very active' },
    { value: 'extra_active', label: 'Extra active' },
];

const FITNESS_GOALS = [
    { value: 'lose_weight', label: 'Lose weight' },
    { value: 'maintain', label: 'Maintain weight' },
    { value: 'gain_muscle', label: 'Gain muscle' },
];

const emptyForm = {
    first_name: '',
    last_name: '',
    age: '',
    gender: 'male',
    height_cm: '',
    weight_kg: '',
    target_weight_kg: '',
    activity_level: 'moderately_active',
    goal: 'maintain',
};

const Profile = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [mealPlan, setMealPlan] = useState([]);
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState('');
    const [profileError, setProfileError] = useState('');
    const [profileSuccess, setProfileSuccess] = useState('');
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [isSavingProfile, setIsSavingProfile] = useState(false);

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
            const profileData = response.data.profile;
            setProfile(profileData);
            if (profileData) {
                setForm({
                    first_name: profileData.first_name || '',
                    last_name: profileData.last_name || '',
                    age: profileData.age ?? '',
                    gender: profileData.gender || 'male',
                    height_cm: profileData.height_cm ?? '',
                    weight_kg: profileData.weight_kg ?? '',
                    target_weight_kg: profileData.target_weight_kg ?? '',
                    activity_level: profileData.activity_level || 'moderately_active',
                    goal: profileData.goal || 'maintain',
                });
            }
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

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setPasswordError('');
        setPasswordSuccess('');

        if (newPassword !== confirmPassword) {
            setPasswordError('Passwords do not match.');
            return;
        }

        setIsChangingPassword(true);
        try {
            const response = await client.post('/users/me/change-password', {
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword,
            });
            setPasswordSuccess(response.data.message);
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (error) {
            const detail = error.response?.data?.detail;
            if (Array.isArray(detail)) {
                setPasswordError(detail.map((item) => item.msg).join(' '));
            } else {
                setPasswordError(typeof detail === 'string' ? detail : 'Unable to change password.');
            }
        } finally {
            setIsChangingPassword(false);
        }
    };

    const handleProfileChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        setProfileError('');
        setProfileSuccess('');
        setIsSavingProfile(true);

        try {
            const response = await client.put('/users/me/profile', {
                first_name: form.first_name.trim() || null,
                last_name: form.last_name.trim() || null,
                age: Number(form.age),
                gender: form.gender,
                height_cm: Number(form.height_cm),
                weight_kg: Number(form.weight_kg),
                target_weight_kg: form.target_weight_kg ? Number(form.target_weight_kg) : null,
                activity_level: form.activity_level,
                goal: form.goal,
            });
            setProfile(response.data);
            setProfileSuccess('Profile updated successfully.');
            fetchMealPlan();
        } catch (error) {
            const detail = error.response?.data?.detail;
            if (Array.isArray(detail)) {
                setProfileError(detail.map((item) => item.msg).join(' '));
            } else {
                setProfileError(typeof detail === 'string' ? detail : 'Unable to update profile.');
            }
        } finally {
            setIsSavingProfile(false);
        }
    };

    const displayName = [form.first_name, form.last_name].filter(Boolean).join(' ')
        || user?.email?.split('@')[0]
        || 'Athlete';

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
                        {(displayName[0] || 'U').toUpperCase()}
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">{displayName}</h1>
                    <p className="text-gray-400">{user?.email}</p>
                    <div className="mt-4 px-3 py-1 bg-white/5 rounded-full text-xs text-brand-primary border border-brand-primary/20 uppercase tracking-widest font-bold">
                        User ID: {user?.id}
                    </div>
                </div>
            </div>

            {/* Profile Sections */}
            <div className="space-y-6">

                {/* Edit Profile */}
                <div className="bg-brand-surface/30 border border-white/5 rounded-2xl p-6">
                    <h2 className="text-lg font-bold text-white mb-4">Edit Profile</h2>

                    {profileError && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-4 text-sm">
                            {profileError}
                        </div>
                    )}

                    {profileSuccess && (
                        <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 px-4 py-3 rounded-lg mb-4 text-sm">
                            {profileSuccess}
                        </div>
                    )}

                    <form onSubmit={handleSaveProfile} className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <FormField label="First Name" name="first_name" value={form.first_name} onChange={handleProfileChange} />
                            <FormField label="Last Name" name="last_name" value={form.last_name} onChange={handleProfileChange} />
                        </div>

                        <InfoItem label="Email Address" value={user?.email} />

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <FormField label="Age" name="age" type="number" min="1" max="120" value={form.age} onChange={handleProfileChange} required />
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2">Gender</label>
                                <select
                                    name="gender"
                                    value={form.gender}
                                    onChange={handleProfileChange}
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                >
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <FormField label="Height (cm)" name="height_cm" type="number" min="1" step="0.1" value={form.height_cm} onChange={handleProfileChange} required />
                            <FormField label="Weight (kg)" name="weight_kg" type="number" min="1" step="0.1" value={form.weight_kg} onChange={handleProfileChange} required />
                            <FormField label="Target Weight (kg)" name="target_weight_kg" type="number" min="1" step="0.1" value={form.target_weight_kg} onChange={handleProfileChange} placeholder="Optional" />
                        </div>

                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2">Activity Level</label>
                            <select
                                name="activity_level"
                                value={form.activity_level}
                                onChange={handleProfileChange}
                                className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                            >
                                {ACTIVITY_LEVELS.map((level) => (
                                    <option key={level.value} value={level.value}>{level.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2">Fitness Goal</label>
                            <select
                                name="goal"
                                value={form.goal}
                                onChange={handleProfileChange}
                                className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                            >
                                {FITNESS_GOALS.map((goalOption) => (
                                    <option key={goalOption.value} value={goalOption.value}>{goalOption.label}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            type="submit"
                            disabled={isSavingProfile || !profile}
                            className={`w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all ${isSavingProfile ? 'opacity-70 cursor-not-allowed' : ''}`}
                        >
                            {isSavingProfile ? 'Saving...' : 'Save Profile'}
                        </button>
                    </form>
                </div>

                {/* Change Password */}
                <div className="bg-brand-surface/30 border border-white/5 rounded-2xl p-6">
                    <h2 className="text-lg font-bold text-white mb-4">Change Password</h2>

                    {passwordError && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg mb-4 text-sm">
                            {passwordError}
                        </div>
                    )}

                    {passwordSuccess && (
                        <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 px-4 py-3 rounded-lg mb-4 text-sm">
                            {passwordSuccess}
                        </div>
                    )}

                    <form onSubmit={handleChangePassword} className="space-y-4">
                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="currentPassword">
                                Current Password
                            </label>
                            <input
                                className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                                id="currentPassword"
                                type="password"
                                value={currentPassword}
                                onChange={(e) => setCurrentPassword(e.target.value)}
                                required
                            />
                        </div>
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
                                Confirm New Password
                            </label>
                            <input
                                className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                                id="confirmPassword"
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                minLength={8}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isChangingPassword}
                            className={`w-full bg-brand-primary hover:bg-emerald-400 text-brand-dark font-bold py-3.5 px-4 rounded-xl transition-all ${isChangingPassword ? 'opacity-70 cursor-not-allowed' : ''}`}
                        >
                            {isChangingPassword ? 'Updating...' : 'Update Password'}
                        </button>
                    </form>
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

const FormField = ({ label, name, value, onChange, type = 'text', required = false, ...props }) => (
    <div>
        <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor={name}>{label}</label>
        <input
            id={name}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            required={required}
            className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
            {...props}
        />
    </div>
);

export default Profile;
