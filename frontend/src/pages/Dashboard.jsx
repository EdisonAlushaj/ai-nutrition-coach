import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';

const FALLBACK_GOALS = {
    daily_calories: 2000,
    protein_g: 150,
    carbs_g: 250,
    fat_g: 70,
};

const FITNESS_GOAL_DISPLAY = {
    lose_weight: {
        label: 'Lose weight',
        subtitle: 'Stay focused on your cut today.',
        badge: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    },
    maintain: {
        label: 'Maintain weight',
        subtitle: "Let's hit those macros today.",
        badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    },
    gain_muscle: {
        label: 'Gain muscle',
        subtitle: 'Fuel your gains today.',
        badge: 'bg-violet-500/15 text-violet-300 border-violet-500/30',
    },
};

const getFitnessGoalDisplay = (goal) =>
    FITNESS_GOAL_DISPLAY[goal] || {
        label: 'Fitness goal not set',
        subtitle: "Let's hit those macros today.",
        badge: 'bg-gray-500/15 text-gray-300 border-gray-500/30',
    };

const getWeightGoalSummary = (current, target, fitnessGoal) => {
    if (!current || !target) return null;

    const currentRounded = Math.round(current * 10) / 10;
    const targetRounded = Math.round(target * 10) / 10;

    if (fitnessGoal === 'lose_weight') {
        if (current <= target) {
            return { label: 'Target weight reached', toGo: 0, progress: 100 };
        }
        const toGo = current - target;
        return {
            label: `${toGo.toFixed(1)} kg to go`,
            toGo,
            progress: Math.min(100, Math.max(0, ((current - target) / current) * 100)),
        };
    }

    if (fitnessGoal === 'gain_muscle') {
        if (current >= target) {
            return { label: 'Target weight reached', toGo: 0, progress: 100 };
        }
        const toGo = target - current;
        return {
            label: `${toGo.toFixed(1)} kg to go`,
            toGo,
            progress: Math.min(100, Math.max(0, (current / target) * 100)),
        };
    }

    const diff = Math.abs(current - target);
    if (diff <= 1) {
        return { label: 'On target weight', toGo: 0, progress: 100 };
    }
    return {
        label: `${diff.toFixed(1)} kg from target`,
        toGo: diff,
        progress: Math.max(0, 100 - diff * 10),
    };
};

const ALERT_STYLES = {
    warning: 'bg-red-500/10 border-red-500/30 text-red-300',
    info: 'bg-amber-500/10 border-amber-500/30 text-amber-200',
};

const STATUS_STYLES = {
    met: {
        bar: 'bg-emerald-500',
        badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
        label: 'Goal met',
    },
    over: {
        bar: 'bg-red-500',
        badge: 'bg-red-500/20 text-red-400 border-red-500/30',
        label: 'Over goal',
    },
    under: {
        bar: 'bg-amber-500',
        badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
        label: 'Under goal',
    },
};

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [analytics, setAnalytics] = useState(null);
    const [weeklyAnalytics, setWeeklyAnalytics] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [logs, setLogs] = useState([]);
    const [fitnessGoal, setFitnessGoal] = useState(null);
    const [nutritionGoals, setNutritionGoals] = useState(FALLBACK_GOALS);
    const [lifetimeProgress, setLifetimeProgress] = useState(null);
    const [motivation, setMotivation] = useState(null);
    const [quoteCooldown, setQuoteCooldown] = useState(false);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        if (!user?.id) return;
        setLoading(true);
        try {
            const [analyticsRes, weeklyRes, alertsRes, logsRes, goalsRes, progressRes, motivationRes] = await Promise.all([
                client.get(`/users/${user.id}/analytics/today`),
                client.get(`/users/${user.id}/analytics/weekly`),
                client.get(`/users/${user.id}/analytics/today/alerts`),
                client.get(`/users/${user.id}/logs/?limit=50`),
                client.get(`/users/${user.id}/nutrition-goals`),
                client.get(`/users/${user.id}/analytics/progress`),
                client.get(`/users/${user.id}/motivation/daily`),
            ]);

            setAnalytics(analyticsRes.data);
            setWeeklyAnalytics(weeklyRes.data);
            setAlerts(alertsRes.data?.alerts || []);
            setLogs(logsRes.data);
            setFitnessGoal(goalsRes.data?.fitness_goal ?? null);
            setNutritionGoals(goalsRes.data ?? FALLBACK_GOALS);
            setLifetimeProgress(progressRes.data);
            setMotivation(motivationRes.data);
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
        } finally {
            setLoading(false);
        }
    }, [user?.id]);

    useEffect(() => {
        fetchData();
    }, [fetchData, location.key]);

    const handleRefreshQuote = async () => {
        if (!user?.id || quoteCooldown) return;
        setQuoteCooldown(true);
        try {
            const response = await client.get(`/users/${user.id}/motivation/random`, {
                params: motivation?.message ? { exclude: motivation.message } : {},
            });
            setMotivation(response.data);
        } catch (err) {
            console.error('Failed to refresh motivation quote:', err);
        } finally {
            setTimeout(() => setQuoteCooldown(false), 2000);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen pt-24 pb-12 px-6 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
            </div>
        );
    }

    const goalCalories = nutritionGoals.daily_calories;
    const goalProtein = nutritionGoals.protein_g;
    const goalCarbs = nutritionGoals.carbs_g;
    const goalFat = nutritionGoals.fat_g;

    const calories = analytics?.total_calories || 0;
    const protein = analytics?.total_protein || 0;
    const carbs = analytics?.total_carbs || 0;
    const fat = analytics?.total_fat || 0;
    const calPercentage = Math.min((calories / goalCalories) * 100, 100);

    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todaysLogs = logs.filter((log) => new Date(log.timestamp) >= todayStart);
    const goalDisplay = getFitnessGoalDisplay(fitnessGoal);
    const weightSummary = getWeightGoalSummary(
        nutritionGoals.current_weight_kg,
        nutritionGoals.target_weight_kg,
        fitnessGoal,
    );

    return (
        <div className="min-h-screen pt-24 pb-24 px-4 md:px-8 max-w-4xl mx-auto">

            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Hello, {user?.email?.split('@')[0] || 'Athlete'}
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">{goalDisplay.subtitle}</p>
                    <span
                        className={`inline-flex mt-3 text-xs font-semibold uppercase tracking-wide px-3 py-1 rounded-full border ${goalDisplay.badge}`}
                    >
                        Goal: {goalDisplay.label}
                    </span>
                    {nutritionGoals.target_weight_kg && (
                        <p className="text-gray-400 text-sm mt-3">
                            Target weight: <span className="text-white font-medium">{Math.round(nutritionGoals.target_weight_kg)} kg</span>
                            {nutritionGoals.current_weight_kg && (
                                <span className="text-gray-500"> · Current: {Math.round(nutritionGoals.current_weight_kg)} kg</span>
                            )}
                        </p>
                    )}
                </div>
                <Link to="/profile" className="bg-brand-surface border border-white/5 rounded-full p-1 pr-4 flex items-center gap-3 hover:bg-white/5 transition-colors group">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center text-xs font-bold group-hover:scale-110 transition-transform">
                        {(user?.email?.[0] || 'U').toUpperCase()}
                    </div>
                    <span className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">Profile</span>
                </Link>
            </header>

            {motivation?.message && (
                <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-2xl p-5 mb-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-24 h-24 bg-brand-accent/10 rounded-full blur-[40px] pointer-events-none" />
                    <div className="relative z-10 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                        <div>
                            <p className="text-xs uppercase tracking-widest text-brand-accent font-semibold mb-2">
                                Daily Motivation
                            </p>
                            <p className="text-white text-base md:text-lg leading-relaxed italic">
                                "{motivation.message}"
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={handleRefreshQuote}
                            disabled={quoteCooldown}
                            className={`flex-shrink-0 text-xs font-semibold uppercase tracking-wide px-4 py-2 rounded-full border transition-all ${
                                quoteCooldown
                                    ? 'border-white/10 text-gray-500 cursor-not-allowed'
                                    : 'border-brand-primary/40 text-brand-primary hover:bg-brand-primary/10'
                            }`}
                        >
                            {quoteCooldown ? 'Wait...' : 'New Quote'}
                        </button>
                    </div>
                </div>
            )}

            {alerts.length > 0 && (
                <div className="space-y-3 mb-8">
                    {alerts.map((alert, index) => (
                        <div
                            key={`${alert.type}-${index}`}
                            className={`rounded-2xl border px-4 py-3 text-sm ${ALERT_STYLES[alert.severity] || ALERT_STYLES.info}`}
                            role="alert"
                        >
                            {alert.message}
                        </div>
                    ))}
                </div>
            )}

            {weightSummary && (
                <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-2xl p-5 mb-8">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                        <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Weight Progress</h2>
                        <span className="text-sm text-brand-primary font-medium">{weightSummary.label}</span>
                    </div>
                    <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden mb-2">
                        <div
                            className="h-full bg-gradient-to-r from-sky-500 to-brand-primary rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${weightSummary.progress}%` }}
                        />
                    </div>
                    <p className="text-xs text-gray-500">
                        {Math.round(nutritionGoals.current_weight_kg)} kg current → {Math.round(nutritionGoals.target_weight_kg)} kg target
                    </p>
                </div>
            )}

            <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden mb-8">
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand-primary/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="flex flex-col md:flex-row gap-8 items-center relative z-10">
                    <div className="relative w-40 h-40 flex-shrink-0">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle cx="50%" cy="50%" r="45%" fill="transparent" stroke="#334155" strokeWidth="8" />
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                fill="transparent"
                                stroke={calPercentage >= 100 ? '#ef4444' : '#10b981'}
                                strokeWidth="8"
                                strokeDasharray="283"
                                strokeDashoffset={283 - (283 * calPercentage) / 100}
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out"
                            />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-3xl font-bold text-white">{Math.round(calories)}</span>
                            <span className="text-xs text-gray-400">/ {Math.round(goalCalories)} kcal</span>
                        </div>
                    </div>

                    <div className="flex-1 w-full space-y-4">
                        <MacroBar label="Protein" value={protein} max={goalProtein} color="bg-blue-500" />
                        <MacroBar label="Carbs" value={carbs} max={goalCarbs} color="bg-orange-500" />
                        <MacroBar label="Fat" value={fat} max={goalFat} color="bg-yellow-500" />
                    </div>
                </div>
            </div>

            {lifetimeProgress && (
                <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl mb-8">
                    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2 mb-5">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <span className="w-1 h-6 bg-brand-primary rounded-full"></span>
                                Lifetime Progress
                            </h2>
                            <p className="text-gray-400 text-sm mt-1">
                                {lifetimeProgress.tracking_since
                                    ? `Tracking since ${new Date(lifetimeProgress.tracking_since).toLocaleDateString()}`
                                    : 'Log your first meal to start tracking progress'}
                            </p>
                        </div>
                        {lifetimeProgress.current_streak > 0 && (
                            <span className="text-xs font-semibold uppercase tracking-wide px-3 py-1 rounded-full border bg-emerald-500/15 text-emerald-300 border-emerald-500/30">
                                {lifetimeProgress.current_streak} day streak
                            </span>
                        )}
                    </div>

                    <div className="mb-4">
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-300 font-medium">Days on calorie goal</span>
                            <span className="text-brand-primary font-bold">{lifetimeProgress.success_rate}%</span>
                        </div>
                        <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-brand-primary to-brand-accent rounded-full transition-all duration-1000 ease-out"
                                style={{ width: `${Math.min(lifetimeProgress.success_rate, 100)}%` }}
                            />
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            {lifetimeProgress.days_goal_met} of {lifetimeProgress.days_tracked} logged days met your{' '}
                            {Math.round(lifetimeProgress.daily_calorie_goal)} kcal target
                        </p>
                    </div>

                    <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="bg-brand-dark/40 rounded-xl p-3 border border-white/5">
                            <p className="text-lg font-bold text-emerald-400">{lifetimeProgress.days_goal_met}</p>
                            <p className="text-[10px] uppercase tracking-wide text-gray-500">On goal</p>
                        </div>
                        <div className="bg-brand-dark/40 rounded-xl p-3 border border-white/5">
                            <p className="text-lg font-bold text-amber-400">{lifetimeProgress.days_under_goal}</p>
                            <p className="text-[10px] uppercase tracking-wide text-gray-500">Under</p>
                        </div>
                        <div className="bg-brand-dark/40 rounded-xl p-3 border border-white/5">
                            <p className="text-lg font-bold text-red-400">{lifetimeProgress.days_over_goal}</p>
                            <p className="text-[10px] uppercase tracking-wide text-gray-500">Over</p>
                        </div>
                    </div>
                </div>
            )}

            {weeklyAnalytics?.days?.length > 0 && (
                <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl mb-8">
                    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2 mb-6">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <span className="w-1 h-6 bg-brand-accent rounded-full"></span>
                                Weekly Summary
                            </h2>
                            <p className="text-gray-400 text-sm mt-1">
                                Last 7 days vs {Math.round(goalCalories)} kcal daily goal
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-7 gap-2 md:gap-3">
                        {weeklyAnalytics.days.map((day) => {
                            const styles = STATUS_STYLES[day.goal_status] || STATUS_STYLES.under;
                            const barHeight = Math.min((day.total_calories / goalCalories) * 100, 100);
                            const dayLabel = new Date(day.date).toLocaleDateString([], { weekday: 'short' });
                            const isToday = day.date === new Date().toISOString().slice(0, 10);

                            return (
                                <div key={day.date} className="flex flex-col items-center gap-2">
                                    <div className="w-full h-28 bg-brand-dark/40 rounded-xl flex items-end justify-center p-2 border border-white/5">
                                        <div
                                            className={`w-full rounded-md transition-all duration-700 ${styles.bar}`}
                                            style={{ height: `${Math.max(barHeight, day.total_calories > 0 ? 8 : 4)}%` }}
                                            title={`${Math.round(day.total_calories)} kcal`}
                                        />
                                    </div>
                                    <div className="text-center">
                                        <p className={`text-xs font-semibold ${isToday ? 'text-brand-primary' : 'text-gray-300'}`}>
                                            {dayLabel}
                                        </p>
                                        <p className="text-[10px] text-gray-500">{Math.round(day.total_calories)}</p>
                                    </div>
                                    <span className={`text-[9px] uppercase tracking-wide px-1.5 py-0.5 rounded-full border ${styles.badge}`}>
                                        {styles.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            <div>
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <span className="w-1 h-6 bg-brand-primary rounded-full"></span>
                    Today's Logs
                </h2>

                <div className="space-y-4">
                    {todaysLogs.length === 0 ? (
                        <div className="text-center py-10 text-gray-500 italic bg-brand-surface/30 rounded-2xl border border-dashed border-white/5">
                            No meals logged today yet.
                        </div>
                    ) : (
                        todaysLogs.map((log) => (
                            <div key={log.id} className="group bg-brand-surface border border-white/5 p-4 rounded-xl flex justify-between items-center hover:border-brand-primary/30 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-gray-800 flex items-center justify-center text-xl">
                                        🍽️
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white group-hover:text-brand-primary transition-colors">
                                            {log.food_name}
                                            {log.is_manual && (
                                                <span className="ml-2 text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                                                    Manual
                                                </span>
                                            )}
                                        </h3>
                                        <div className="text-xs text-gray-400 flex gap-2">
                                            <span>
                                                {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
                />
            </div>
        </div>
    );
};

export default Dashboard;
