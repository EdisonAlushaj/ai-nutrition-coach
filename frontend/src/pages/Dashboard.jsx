import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [analytics, setAnalytics] = useState(null);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!user?.id) return;
            setLoading(true);
            try {
                // Fetch analytics for today and recent logs
                const [analyticsRes, logsRes] = await Promise.all([
                    client.get(`/users/${user.id}/analytics/today`),
                    client.get(`/users/${user.id}/logs/?limit=50`)
                ]);

                console.log("Analytics Data:", analyticsRes.data);
                setAnalytics(analyticsRes.data);
                setLogs(logsRes.data);
            } catch (err) {
                console.error("Failed to fetch dashboard data:", err);
            } finally {
                setLoading(false);
            }
        };

        if (user?.id) {
            fetchData();
        }
    }, [user?.id]);

    if (loading) {
        return (
            <div className="min-h-screen pt-24 pb-12 px-6 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
            </div>
        );
    }

    // Default values if no data
    const calories = analytics?.total_calories || 0;
    const protein = analytics?.total_protein || 0;
    const carbs = analytics?.total_carbs || 0;
    const fat = analytics?.total_fat || 0;

    // Goals (hardcoded for now, ideal: fetch from user profile)
    const GOAL_CALORIES = 2000;
    const GOAL_PROTEIN = 150;
    const GOAL_CARBS = 250;
    const GOAL_FAT = 70;

    const calPercentage = Math.min((calories / GOAL_CALORIES) * 100, 100);

    return (
        <div className="min-h-screen pt-24 pb-24 px-4 md:px-8 max-w-4xl mx-auto">

            {/* Header */}
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Hello, {user?.name || 'Athlete'}
                    </h1>
                    <p className="text-gray-400 text-sm">Let's hit those macros today.</p>
                </div>
                <Link to="/profile" className="bg-brand-surface border border-white/5 rounded-full p-1 pr-4 flex items-center gap-3 hover:bg-white/5 transition-colors group">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center text-xs font-bold group-hover:scale-110 transition-transform">
                        {user?.name?.[0] || 'U'}
                    </div>
                    <span className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">Profile</span>
                </Link>
            </header>

            {/* Daily Summary Card */}
            <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden mb-8">
                {/* Background Glow */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand-primary/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="flex flex-col md:flex-row gap-8 items-center relative z-10">

                    {/* Calorie Ring */}
                    <div className="relative w-40 h-40 flex-shrink-0">
                        <svg className="w-full h-full transform -rotate-90">
                            {/* Background Circle */}
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                fill="transparent"
                                stroke="#334155" // Slate 700
                                strokeWidth="8"
                            />
                            {/* Progress Circle */}
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                fill="transparent"
                                stroke={calPercentage > 100 ? '#ef4444' : '#10b981'}
                                strokeWidth="8"
                                strokeDasharray="283" // 2 * pi * 45%
                                strokeDashoffset={283 - (283 * calPercentage) / 100}
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out"
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-3xl font-bold text-white">{Math.round(calories)}</span>
                            <span className="text-xs text-gray-400">/ {GOAL_CALORIES} kcal</span>
                        </div>
                    </div>

                    {/* Macros Bars */}
                    <div className="flex-1 w-full space-y-4">
                        <MacroBar label="Protein" value={protein} max={GOAL_PROTEIN} color="bg-blue-500" />
                        <MacroBar label="Carbs" value={carbs} max={GOAL_CARBS} color="bg-orange-500" />
                        <MacroBar label="Fat" value={fat} max={GOAL_FAT} color="bg-yellow-500" />
                    </div>
                </div>
            </div>

            {/* Today's Meals Timeline */}
            <div>
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <span className="w-1 h-6 bg-brand-primary rounded-full"></span>
                    Today's Logs
                </h2>

                <div className="space-y-4">
                    {logs.length === 0 ? (
                        <div className="text-center py-10 text-gray-500 italic bg-brand-surface/30 rounded-2xl border border-dashed border-white/5">
                            No meals logged today yet.
                        </div>
                    ) : (
                        logs.map((log) => (
                            <div key={log.id} className="group bg-brand-surface border border-white/5 p-4 rounded-xl flex justify-between items-center hover:border-brand-primary/30 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-gray-800 flex items-center justify-center text-xl">
                                        🍽️
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white group-hover:text-brand-primary transition-colors">{log.food_name}</h3>
                                        <div className="text-xs text-gray-400 flex gap-2">
                                            <span>
                                                {new Date(log.timestamp).toLocaleDateString() === new Date().toLocaleDateString()
                                                    ? new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                                    : new Date(log.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
                                                }
                                            </span>
                                            <span>•</span>
                                            <span className="text-brand-primary">{log.calories_consumed} kcal</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right text-xs text-gray-500 hidden sm:block">
                                    <div>P: {log.protein_g}g</div>
                                    <div>C: {log.carbs_g}g</div>
                                    <div>F: {log.fat_g}g</div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Floating Action Button */}
            <button
                className="fixed bottom-8 right-8 w-14 h-14 bg-brand-primary hover:bg-brand-primary/90 text-brand-dark rounded-full shadow-lg shadow-brand-primary/40 flex items-center justify-center text-3xl font-bold transition-transform hover:scale-110 active:scale-95"
                aria-label="Add Food"
                onClick={() => navigate('/recognize')}
            >
                +
            </button>
        </div>
    );
};

const MacroBar = ({ label, value, max, color }) => {
    const percentage = Math.min((value / max) * 100, 100);
    return (
        <div>
            <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-medium">{label}</span>
                <span className="text-gray-500">{Math.round(value)} / {max}g</span>
            </div>
            <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
                <div
                    className={`h-full ${color} rounded-full transition-all duration-1000 ease-out`}
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
        </div>
    );
};

export default Dashboard;
