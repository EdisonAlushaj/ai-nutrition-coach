import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext';
import BarcodeScanner from '../components/BarcodeScanner';

const EMPTY_MANUAL_FORM = {
    food_name: '',
    calories_consumed: '',
    protein_g: '',
    carbs_g: '',
    fat_g: '',
};

const FoodRecognition = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [viewMode, setViewMode] = useState('ai');
    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [logging, setLogging] = useState(false);
    const [error, setError] = useState(null);
    const [manualForm, setManualForm] = useState(EMPTY_MANUAL_FORM);
    const [manualError, setManualError] = useState('');
    const [barcodeInput, setBarcodeInput] = useState('');
    const [barcodeProduct, setBarcodeProduct] = useState(null);
    const [barcodeError, setBarcodeError] = useState('');
    const [scanning, setScanning] = useState(false);
    const [lookingUpBarcode, setLookingUpBarcode] = useState(false);

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            setError('Please select a JPG or PNG image.');
            return;
        }

        setSelectedImage(file);
        setPreviewUrl(URL.createObjectURL(file));
        setPredictions([]);
        setError(null);
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
            setError("Failed to recognize food. Try a clearer image or enter manually.");
        } finally {
            setLoading(false);
        }
    };

    const handleLogFood = async (label) => {
        if (!user?.id) return;
        setLogging(true);
        setError(null);

        try {
            const searchRes = await client.get(`/search-food?name=${encodeURIComponent(label)}`);
            const foodData = searchRes.data[0];

            if (!foodData) {
                setError(`Could not find nutritional data for ${label}. Try manual entry.`);
                setLogging(false);
                return;
            }

            await client.post(`/users/${user.id}/logs`, {
                food_name: foodData.name,
                calories_consumed: foodData.total_calories,
                protein_g: foodData.protein_g,
                carbs_g: foodData.carbs_g,
                fat_g: foodData.fat_g,
                meal_id: foodData.id,
                is_manual: false,
            });

            navigate('/dashboard');
        } catch (err) {
            console.error("Logging failed:", err);
            setError("Failed to log food. Try manual entry instead.");
        } finally {
            setLogging(false);
        }
    };

    const openManualEntry = (prefillName = '') => {
        setViewMode('manual');
        setManualError('');
        setManualForm({
            ...EMPTY_MANUAL_FORM,
            food_name: prefillName ? prefillName.replace(/_/g, ' ') : '',
        });
    };

    const updateManualField = (field, value) => {
        setManualForm((prev) => ({ ...prev, [field]: value }));
    };

    const validateManualForm = () => {
        if (!manualForm.food_name.trim()) {
            return 'Food name is required.';
        }

        const numericFields = ['calories_consumed', 'protein_g', 'carbs_g', 'fat_g'];
        for (const field of numericFields) {
            const value = Number(manualForm[field]);
            if (Number.isNaN(value) || value <= 0) {
                return 'All nutrition fields must be positive numbers.';
            }
        }

        return null;
    };

    const handleManualSubmit = async (e) => {
        e.preventDefault();
        setManualError('');

        const validationMessage = validateManualForm();
        if (validationMessage) {
            setManualError(validationMessage);
            return;
        }

        if (!user?.id) return;

        setLogging(true);
        try {
            await client.post(`/users/${user.id}/logs`, {
                food_name: manualForm.food_name.trim(),
                calories_consumed: Number(manualForm.calories_consumed),
                protein_g: Number(manualForm.protein_g),
                carbs_g: Number(manualForm.carbs_g),
                fat_g: Number(manualForm.fat_g),
                is_manual: true,
            });
            navigate('/dashboard');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setManualError(detail.map((item) => item.msg).join(' '));
            } else {
                setManualError(typeof detail === 'string' ? detail : 'Failed to save manual entry.');
            }
        } finally {
            setLogging(false);
        }
    };

    const lookupBarcode = async (rawBarcode) => {
        const barcode = rawBarcode.trim();
        if (!barcode) {
            setBarcodeError('Enter or scan a barcode first.');
            return;
        }

        setLookingUpBarcode(true);
        setBarcodeError('');
        setBarcodeProduct(null);
        setScanning(false);

        try {
            const response = await client.get(`/foods/barcode/${encodeURIComponent(barcode)}`);
            setBarcodeProduct(response.data);
            setBarcodeInput(response.data.barcode);
        } catch (err) {
            const detail = err.response?.data?.detail;
            setBarcodeError(typeof detail === 'string' ? detail : 'Product not found for this barcode.');
        } finally {
            setLookingUpBarcode(false);
        }
    };

    const handleBarcodeDetected = (code) => {
        setBarcodeInput(code);
        lookupBarcode(code);
    };

    const handleLogBarcodeFood = async () => {
        if (!user?.id || !barcodeProduct) return;

        setLogging(true);
        setBarcodeError('');
        try {
            await client.post(`/users/${user.id}/logs`, {
                food_name: barcodeProduct.food_name,
                calories_consumed: barcodeProduct.calories_consumed,
                protein_g: barcodeProduct.protein_g,
                carbs_g: barcodeProduct.carbs_g,
                fat_g: barcodeProduct.fat_g,
                is_manual: false,
            });
            navigate('/dashboard');
        } catch (err) {
            setBarcodeError('Failed to log scanned food. Try again or use manual entry.');
        } finally {
            setLogging(false);
        }
    };

    const openBarcodeMode = () => {
        setViewMode('barcode');
        setBarcodeError('');
        setBarcodeProduct(null);
        setScanning(true);
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 md:px-8 max-w-4xl mx-auto">

            <header className="mb-8">
                <Link
                    to="/dashboard"
                    className="text-gray-400 hover:text-brand-primary transition-colors flex items-center gap-2 mb-2 text-sm"
                >
                    <span>←</span> Back
                </Link>
                <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Log Food</h1>
                        <p className="text-gray-400">Scan a barcode, use AI, or enter nutrition manually.</p>
                    </div>
                    <div className="flex flex-wrap rounded-xl bg-brand-surface/50 border border-white/10 p-1">
                        <button
                            type="button"
                            onClick={() => setViewMode('ai')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${viewMode === 'ai' ? 'bg-brand-primary text-brand-dark' : 'text-gray-400 hover:text-white'}`}
                        >
                            AI Scan
                        </button>
                        <button
                            type="button"
                            onClick={openBarcodeMode}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${viewMode === 'barcode' ? 'bg-brand-primary text-brand-dark' : 'text-gray-400 hover:text-white'}`}
                        >
                            Barcode
                        </button>
                        <button
                            type="button"
                            onClick={() => openManualEntry()}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${viewMode === 'manual' ? 'bg-brand-primary text-brand-dark' : 'text-gray-400 hover:text-white'}`}
                        >
                            Manual Entry
                        </button>
                    </div>
                </div>
            </header>

            {viewMode === 'ai' ? (
                <div className="grid md:grid-cols-2 gap-8 items-start">
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
                                accept="image/jpeg,image/jpg,image/png"
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

                        <button
                            type="button"
                            onClick={() => openManualEntry()}
                            className="w-full mt-3 py-3 rounded-2xl border border-white/10 text-gray-300 hover:text-white hover:border-brand-primary/40 transition-colors text-sm font-medium"
                        >
                            Skip AI — enter manually
                        </button>
                    </div>

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
                                {predictions[0].confidence < 0.25 && (
                                    <div className="p-4 bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs rounded-xl mb-4 flex items-center gap-3">
                                        <span className="text-xl">⚠️</span>
                                        <span>AI confidence is low. Verify the suggestions or enter manually.</span>
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
                                <button
                                    type="button"
                                    onClick={() => openManualEntry(predictions[0]?.label || '')}
                                    className="w-full py-3 rounded-2xl border border-dashed border-white/10 text-gray-400 hover:text-brand-primary hover:border-brand-primary/40 transition-colors text-sm"
                                >
                                    None of these? Enter manually
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            ) : viewMode === 'barcode' ? (
                <div className="max-w-xl mx-auto bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl space-y-6">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-2">Scan Barcode</h2>
                        <p className="text-gray-400 text-sm">Point your camera at a product barcode or enter the number manually.</p>
                    </div>

                    {scanning && !barcodeProduct && (
                        <BarcodeScanner
                            active={scanning && viewMode === 'barcode'}
                            onDetected={handleBarcodeDetected}
                            onError={setBarcodeError}
                        />
                    )}

                    <div className="flex gap-2">
                        <input
                            type="text"
                            inputMode="numeric"
                            className="flex-1 bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                            placeholder="Enter barcode number"
                            value={barcodeInput}
                            onChange={(e) => setBarcodeInput(e.target.value)}
                        />
                        <button
                            type="button"
                            onClick={() => lookupBarcode(barcodeInput)}
                            disabled={lookingUpBarcode}
                            className="px-5 py-3 rounded-xl bg-brand-primary text-brand-dark font-bold disabled:opacity-60"
                        >
                            {lookingUpBarcode ? '...' : 'Look up'}
                        </button>
                    </div>

                    {!scanning && !barcodeProduct && (
                        <button
                            type="button"
                            onClick={() => setScanning(true)}
                            className="w-full py-3 rounded-2xl border border-white/10 text-gray-300 hover:text-white hover:border-brand-primary/40 transition-colors text-sm font-medium"
                        >
                            Start camera scanner
                        </button>
                    )}

                    {barcodeError && (
                        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-xl">
                            {barcodeError}
                        </div>
                    )}

                    {barcodeProduct && (
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-4">
                            <div>
                                <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Scanned product</p>
                                <h3 className="text-lg font-bold text-white">{barcodeProduct.food_name}</h3>
                                {barcodeProduct.brand && (
                                    <p className="text-sm text-gray-400">{barcodeProduct.brand}</p>
                                )}
                                <p className="text-xs text-gray-500 mt-1">Barcode: {barcodeProduct.barcode}</p>
                            </div>
                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="bg-brand-dark/40 rounded-lg p-3">
                                    <span className="text-gray-400 block">Calories</span>
                                    <span className="text-white font-bold">{barcodeProduct.calories_consumed} kcal</span>
                                </div>
                                <div className="bg-brand-dark/40 rounded-lg p-3">
                                    <span className="text-gray-400 block">Protein</span>
                                    <span className="text-white font-bold">{barcodeProduct.protein_g} g</span>
                                </div>
                                <div className="bg-brand-dark/40 rounded-lg p-3">
                                    <span className="text-gray-400 block">Carbs</span>
                                    <span className="text-white font-bold">{barcodeProduct.carbs_g} g</span>
                                </div>
                                <div className="bg-brand-dark/40 rounded-lg p-3">
                                    <span className="text-gray-400 block">Fat</span>
                                    <span className="text-white font-bold">{barcodeProduct.fat_g} g</span>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={handleLogBarcodeFood}
                                disabled={logging}
                                className={`w-full py-4 rounded-2xl font-bold text-lg bg-brand-primary text-brand-dark hover:scale-[1.02] transition-all ${logging ? 'opacity-70 cursor-not-allowed' : ''}`}
                            >
                                {logging ? 'Logging...' : 'Log to Today'}
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setBarcodeProduct(null);
                                    setScanning(true);
                                    setBarcodeInput('');
                                }}
                                className="w-full py-3 rounded-2xl border border-white/10 text-gray-400 hover:text-white text-sm"
                            >
                                Scan another
                            </button>
                        </div>
                    )}

                    <p className="text-xs text-gray-500 text-center">
                        Demo barcodes: 1234567890123, 4001686341234
                    </p>
                </div>
            ) : (
                <div className="max-w-xl mx-auto bg-brand-surface/50 backdrop-blur-md border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl">
                    <h2 className="text-xl font-bold text-white mb-2">Manual Food Entry</h2>
                    <p className="text-gray-400 text-sm mb-6">Enter the food name and nutrition values yourself.</p>

                    {manualError && (
                        <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-xl">
                            {manualError}
                        </div>
                    )}

                    <form onSubmit={handleManualSubmit} className="space-y-4">
                        <div>
                            <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="food_name">
                                Food Name
                            </label>
                            <input
                                id="food_name"
                                type="text"
                                className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                placeholder="e.g. Grilled chicken salad"
                                value={manualForm.food_name}
                                onChange={(e) => updateManualField('food_name', e.target.value)}
                                required
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="calories">
                                    Calories (kcal)
                                </label>
                                <input
                                    id="calories"
                                    type="number"
                                    min="0.1"
                                    step="0.1"
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                    value={manualForm.calories_consumed}
                                    onChange={(e) => updateManualField('calories_consumed', e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="protein">
                                    Protein (g)
                                </label>
                                <input
                                    id="protein"
                                    type="number"
                                    min="0.1"
                                    step="0.1"
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                    value={manualForm.protein_g}
                                    onChange={(e) => updateManualField('protein_g', e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="carbs">
                                    Carbs (g)
                                </label>
                                <input
                                    id="carbs"
                                    type="number"
                                    min="0.1"
                                    step="0.1"
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                    value={manualForm.carbs_g}
                                    onChange={(e) => updateManualField('carbs_g', e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="fat">
                                    Fat (g)
                                </label>
                                <input
                                    id="fat"
                                    type="number"
                                    min="0.1"
                                    step="0.1"
                                    className="w-full bg-brand-dark/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
                                    value={manualForm.fat_g}
                                    onChange={(e) => updateManualField('fat_g', e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={logging}
                            className={`w-full py-4 rounded-2xl font-bold text-lg bg-brand-primary text-brand-dark hover:scale-[1.02] transition-all ${logging ? 'opacity-70 cursor-not-allowed' : ''}`}
                        >
                            {logging ? 'Saving...' : 'Log Food'}
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default FoodRecognition;
