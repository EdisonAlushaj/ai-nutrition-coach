import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';

const FoodRecognition = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [logging, setLogging] = useState(false);
    const [error, setError] = useState(null);

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedImage(file);
            setPreviewUrl(URL.createObjectURL(file));
            setPredictions([]);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!selectedImage) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', selectedImage);

        try {
            const response = await client.post('/recognize-food', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setPredictions(response.data.predictions);
        } catch (err) {
            console.error("Recognition failed:", err);
            setError("Failed to recognize food. Please try with a clearer image.");
        } finally {
            setLoading(false);
        }
    };

    const handleLogFood = async (label) => {
        if (!user?.id) return;
        setLogging(true);

        try {
            // 1. Search for nutrition data for the recognized label
            const searchRes = await client.get(`/search-food?name=${label}`);
            const foodData = searchRes.data[0]; // Take top search result

            if (!foodData) {
                setError(`Could not find nutritional data for ${label}`);
                setLogging(false);
                return;
            }

            // 2. Log it to the database
            await client.post(`/users/${user.id}/logs`, {
                food_name: foodData.name,
                calories_consumed: foodData.total_calories,
                protein_g: foodData.protein_g,
                carbs_g: foodData.carbs_g,
                fat_g: foodData.fat_g,
                meal_id: foodData.id
            });

            // 3. Success! Go back to dashboard
            navigate('/dashboard');
        } catch (err) {
            console.error("Logging failed:", err);
            setError("Failed to log food. Please try searching manually.");
        } finally {
            setLogging(false);
        }
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 md:px-8 max-w-4xl mx-auto">

            {/* Header */}
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <Link
                        to="/dashboard"
                        className="text-gray-400 hover:text-brand-primary transition-colors flex items-center gap-2 mb-2 text-sm"
                    >
                        <span>←</span> Back
                    </Link>
                    <h1 className="text-3xl font-bold text-white">Snap & Log</h1>
                    <p className="text-gray-400">Identify your meal using AI.</p>
                </div>
            </header>

            <div className="grid md:grid-cols-2 gap-8 items-start">

                {/* Upload Section */}
                <div className="bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 shadow-2xl overflow-hidden">
                    <div className="aspect-square bg-white/5 rounded-2xl flex flex-col items-center justify-center relative group cursor-pointer border-2 border-dashed border-white/10 hover:border-brand-primary/40 transition-all overflow-hidden">
                        {previewUrl ? (
                            <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                        ) : (
                            <>
                                <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">📸</div>
                                <span className="text-gray-400 font-medium">Select Image</span>
                                <span className="text-gray-600 text-xs mt-2">JPG, PNG supported</span>
                            </>
                        )}
                        <input
                            type="file"
                            accept="image/*"
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={handleImageChange}
                        />
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={!selectedImage || loading}
                        className={`w-full mt-6 py-4 rounded-2xl font-bold text-lg transition-all shadow-xl flex items-center justify-center gap-2 ${!selectedImage
                            ? 'bg-gray-700/30 text-gray-500 cursor-not-allowed'
                            : 'bg-brand-primary text-brand-dark hover:scale-[1.02] active:scale-[0.98] shadow-brand-primary/20'
                            }`}
                    >
                        {loading ? (
                            <><div className="animate-spin rounded-full h-5 w-5 border-t-2 border-brand-dark"></div> Analyzing...</>
                        ) : (
                            'Analyze Food'
                        )}
                    </button>

                    {error && (
                        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-xl">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Section */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <span className="w-1 h-6 bg-brand-accent rounded-full"></span>
                        AI Predictions
                    </h2>

                    {predictions.length === 0 ? (
                        <div className="bg-brand-surface/20 border border-dashed border-white/5 rounded-3xl h-64 flex flex-col items-center justify-center text-gray-500 italic p-8 text-center">
                            {loading ? "Warming up the AI engine..." : "Upload a photo to see what our AI thinks it is."}
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Low Confidence Warning */}
                            {predictions[0].confidence < 0.25 && (
                                <div className="p-4 bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs rounded-xl mb-4 flex items-center gap-3">
                                    <span className="text-xl">⚠️</span>
                                    <span>AI confidence is low. Please verify the suggestions or try a clearer photo.</span>
                                </div>
                            )}
                            {predictions.map((pred, index) => (
                                <button
                                    key={index}
                                    onClick={() => handleLogFood(pred.label)}
                                    disabled={logging}
                                    className="w-full bg-brand-surface/40 hover:bg-brand-surface border border-white/5 p-5 rounded-2xl flex justify-between items-center group transition-all text-left disabled:opacity-50"
                                >
                                    <div className="flex-1">
                                        <div className="flex justify-between items-end mb-2">
                                            <h3 className="text-lg font-bold text-white capitalize group-hover:text-brand-primary transition-colors">
                                                {pred.label.replace(/_/g, ' ')}
                                            </h3>
                                            <span className="text-xs font-bold text-brand-accent">
                                                {Math.round(pred.confidence * 100)}% Match
                                            </span>
                                        </div>
                                        {/* Confidence bar */}
                                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-brand-primary to-brand-accent rounded-full transition-all duration-1000"
                                                style={{ width: `${pred.confidence * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-6 w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-xl group-hover:bg-brand-primary group-hover:text-brand-dark transition-all">
                                        {logging ? '⏳' : '→'}
                                    </div>
                                </button>
                            ))}
                            <p className="text-xs text-gray-500 text-center mt-4">
                                Click a label to fetch nutrition info and log it to your dashboard.
                            </p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default FoodRecognition;
