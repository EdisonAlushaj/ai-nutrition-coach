import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const AdminDashboard = () => {
    const { user } = useAuth();
    const [users, setUsers] = useState([]);
    const [ingredients, setIngredients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('users');

    // Form states
    const [ingredientForm, setIngredientForm] = useState({
        name: '',
        calories_per_100g: '',
        protein_per_100g: '',
        carbs_per_100g: '',
        fat_per_100g: ''
    });

    const [mealForm, setMealForm] = useState({
        name: '',
        description: '',
        total_calories: '',
        total_protein: '',
        total_carbs: '',
        total_fat: '',
        ingredient_ids: ''
    });

    const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

    useEffect(() => {
        if (user?.role === 'admin') {
            fetchData();
        }
    }, [user]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [usersRes, ingredientsRes] = await Promise.all([
                client.get('/admin/users'),
                client.get('/ingredients')
            ]);
            setUsers(usersRes.data);
            setIngredients(ingredientsRes.data);
        } catch (error) {
            console.error("Failed to fetch admin data:", error);
            setStatusMsg({ type: 'error', text: 'Failed to load dashboard data.' });
        } finally {
            setLoading(false);
        }
    };

    const handlePromote = async (userId) => {
        try {
            await client.put(`/admin/users/${userId}/promote`);
            setStatusMsg({ type: 'success', text: `User ${userId} promoted to admin!` });
            fetchUsers(); // Refresh user list
        } catch (error) {
            setStatusMsg({ type: 'error', text: 'Failed to promote user.' });
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await client.get('/admin/users');
            setUsers(res.data);
        } catch (error) {
            console.error("Failed to refresh users:", error);
        }
    };

    const handleIngredientSubmit = async (e) => {
        e.preventDefault();
        try {
            await client.post('/admin/ingredients', {
                ...ingredientForm,
                calories_per_100g: parseFloat(ingredientForm.calories_per_100g),
                protein_per_100g: parseFloat(ingredientForm.protein_per_100g),
                carbs_per_100g: parseFloat(ingredientForm.carbs_per_100g),
                fat_per_100g: parseFloat(ingredientForm.fat_per_100g),
            });
            setStatusMsg({ type: 'success', text: 'Ingredient added successfully!' });
            setIngredientForm({
                name: '',
                calories_per_100g: '',
                protein_per_100g: '',
                carbs_per_100g: '',
                fat_per_100g: ''
            });
            fetchData(); // Refresh list to see new ingredient
        } catch (error) {
            setStatusMsg({ type: 'error', text: 'Failed to add ingredient.' });
        }
    };

    const handleMealSubmit = async (e) => {
        e.preventDefault();
        try {
            const ingredientIds = mealForm.ingredient_ids
                ? mealForm.ingredient_ids.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
                : [];

            await client.post('/admin/meals', {
                ...mealForm,
                total_calories: parseFloat(mealForm.total_calories),
                total_protein: parseFloat(mealForm.total_protein),
                total_carbs: parseFloat(mealForm.total_carbs),
                total_fat: parseFloat(mealForm.total_fat),
                ingredient_ids: ingredientIds
            });
            setStatusMsg({ type: 'success', text: 'Meal created successfully!' });
            setMealForm({
                name: '',
                description: '',
                total_calories: '',
                total_protein: '',
                total_carbs: '',
                total_fat: '',
                ingredient_ids: ''
            });
        } catch (error) {
            setStatusMsg({ type: 'error', text: 'Failed to create meal.' });
        }
    };

    if (user?.role !== 'admin') {
        return <Navigate to="/dashboard" />;
    }

    return (
        <div className="min-h-screen pt-24 pb-12 px-6 bg-[#0B0F1A] text-white">
            <div className="container mx-auto">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-12">
                    <div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-primary to-emerald-400 bg-clip-text text-transparent">
                            Admin Control Center
                        </h1>
                        <p className="text-gray-400 mt-2">Manage users and platform content</p>
                    </div>
                    {statusMsg.text && (
                        <div className={`mt-4 md:mt-0 px-6 py-3 rounded-xl border ${statusMsg.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'
                            } backdrop-blur-md`}>
                            {statusMsg.text}
                        </div>
                    )}
                </div>

                {/* Tabs */}
                <div className="flex space-x-4 mb-8">
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${activeTab === 'users'
                                ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20'
                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        User Management
                    </button>
                    <button
                        onClick={() => setActiveTab('cms')}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${activeTab === 'cms'
                                ? 'bg-brand-primary text-white shadow-lg shadow-brand-primary/20'
                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        Food CMS
                    </button>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-primary"></div>
                    </div>
                ) : (
                    <div className="space-y-8 animate-fadeIn">
                        {activeTab === 'users' && (
                            <div className="bg-white/5 rounded-3xl border border-white/10 overflow-hidden backdrop-blur-md">
                                <div className="p-6 border-b border-white/10">
                                    <h2 className="text-xl font-bold">Registered Users</h2>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left">
                                        <thead>
                                            <tr className="bg-white/5 text-gray-400 text-sm uppercase tracking-wider">
                                                <th className="px-6 py-4 font-semibold">ID</th>
                                                <th className="px-6 py-4 font-semibold">Email</th>
                                                <th className="px-6 py-4 font-semibold">Role</th>
                                                <th className="px-6 py-4 font-semibold">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5 text-gray-300">
                                            {users.map(u => (
                                                <tr key={u.id} className="hover:bg-white/5 transition-colors">
                                                    <td className="px-6 py-4">#{u.id}</td>
                                                    <td className="px-6 py-4 font-medium text-white">{u.email}</td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${u.role === 'admin' ? 'bg-brand-primary/20 text-brand-primary' : 'bg-gray-500/20 text-gray-400'
                                                            }`}>
                                                            {u.role}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        {u.role !== 'admin' && (
                                                            <button
                                                                onClick={() => handlePromote(u.id)}
                                                                className="text-emerald-400 hover:text-emerald-300 text-sm font-semibold underline underline-offset-4"
                                                            >
                                                                Promote to Admin
                                                            </button>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {activeTab === 'cms' && (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Add Ingredient */}
                                <div className="bg-white/5 p-8 rounded-3xl border border-white/10 backdrop-blur-md">
                                    <h2 className="text-2xl font-bold mb-6 flex items-center">
                                        <span className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mr-3 text-lg">🍎</span>
                                        Add Ingredient
                                    </h2>
                                    <form onSubmit={handleIngredientSubmit} className="space-y-4">
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-2">Ingredient Name</label>
                                            <input
                                                type="text"
                                                required
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                placeholder="e.g. Avocado"
                                                value={ingredientForm.name}
                                                onChange={e => setIngredientForm({ ...ingredientForm, name: e.target.value })}
                                            />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Calories (100g)</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={ingredientForm.calories_per_100g}
                                                    onChange={e => setIngredientForm({ ...ingredientForm, calories_per_100g: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Protein (100g)</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={ingredientForm.protein_per_100g}
                                                    onChange={e => setIngredientForm({ ...ingredientForm, protein_per_100g: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Carbs (100g)</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={ingredientForm.carbs_per_100g}
                                                    onChange={e => setIngredientForm({ ...ingredientForm, carbs_per_100g: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Fat (100g)</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={ingredientForm.fat_per_100g}
                                                    onChange={e => setIngredientForm({ ...ingredientForm, fat_per_100g: e.target.value })}
                                                />
                                            </div>
                                        </div>
                                        <button className="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-4 rounded-xl shadow-lg shadow-emerald-500/20 transition-all active:scale-[0.98] mt-4">
                                            Save Ingredient
                                        </button>
                                    </form>
                                </div>

                                {/* Create Meal */}
                                <div className="bg-white/5 p-8 rounded-3xl border border-white/10 backdrop-blur-md">
                                    <h2 className="text-2xl font-bold mb-6 flex items-center">
                                        <span className="w-8 h-8 rounded-lg bg-brand-primary/20 text-brand-primary flex items-center justify-center mr-3 text-lg">🥗</span>
                                        Create Meal
                                    </h2>
                                    <form onSubmit={handleMealSubmit} className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="col-span-2">
                                                <label className="block text-sm text-gray-400 mb-2">Meal Name</label>
                                                <input
                                                    type="text" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    placeholder="e.g. Chicken Salad"
                                                    value={mealForm.name}
                                                    onChange={e => setMealForm({ ...mealForm, name: e.target.value })}
                                                />
                                            </div>
                                            <div className="col-span-2">
                                                <label className="block text-sm text-gray-400 mb-2">Description</label>
                                                <textarea
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors h-20"
                                                    value={mealForm.description}
                                                    onChange={e => setMealForm({ ...mealForm, description: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Total Calories</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={mealForm.total_calories}
                                                    onChange={e => setMealForm({ ...mealForm, total_calories: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Protein</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={mealForm.total_protein}
                                                    onChange={e => setMealForm({ ...mealForm, total_protein: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Carbs</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={mealForm.total_carbs}
                                                    onChange={e => setMealForm({ ...mealForm, total_carbs: e.target.value })}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-400 mb-2">Fat</label>
                                                <input
                                                    type="number" step="0.1" required
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    value={mealForm.total_fat}
                                                    onChange={e => setMealForm({ ...mealForm, total_fat: e.target.value })}
                                                />
                                            </div>
                                            <div className="col-span-2">
                                                <label className="block text-sm text-gray-400 mb-2">Ingredient IDs (comma separated)</label>
                                                <input
                                                    type="text"
                                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:border-brand-primary outline-none transition-colors"
                                                    placeholder="1, 2, 3"
                                                    value={mealForm.ingredient_ids}
                                                    onChange={e => setMealForm({ ...mealForm, ingredient_ids: e.target.value })}
                                                />
                                                <div className="mt-2 text-[10px] text-gray-500 max-h-20 overflow-y-auto bg-black/20 p-2 rounded">
                                                    Available IDs: {ingredients.map(i => `${i.id}(${i.name})`).join(', ')}
                                                </div>
                                            </div>
                                        </div>
                                        <button className="w-full bg-brand-primary hover:bg-brand-secondary text-white font-bold py-4 rounded-xl shadow-lg shadow-brand-primary/20 transition-all active:scale-[0.98] mt-4">
                                            Create Meal
                                        </button>
                                    </form>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
