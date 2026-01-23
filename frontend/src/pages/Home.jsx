import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div className="relative min-h-screen pt-20"> {/* pt-20 to account for fixed navbar */}
            {/* Background Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-brand-primary/20 blur-[120px] rounded-full pointer-events-none"></div>

            {/* Hero Section */}
            <div className="container mx-auto px-6 py-20 text-center relative z-10">
                <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight tracking-tight">
                    Master Your <span className="bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">Nutrition</span>
                    <br /> Unlock Your Potential.
                </h1>
                <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                    The AI-powered coach that creates personalized meal plans aimed at your specific fitness goals. Eat smarter, not harder.
                </p>
                <div className="flex justify-center gap-6">
                    <Link to="/register" className="bg-white text-brand-dark px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition-transform transform hover:scale-105 shadow-xl">
                        Get Started Free
                    </Link>
                    <button className="px-8 py-4 rounded-full font-bold text-lg text-white border border-white/20 hover:bg-white/10 transition-colors backdrop-blur-sm">
                        Learn More
                    </button>
                </div>
            </div>

            {/* Feature Grid */}
            <div className="container mx-auto px-6 py-20">
                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        title="AI Analysis"
                        desc="Snap a photo of your food and let our advanced AI calculate macros instantly."
                        icon="📸"
                    />
                    <FeatureCard
                        title="Smart Planning"
                        desc="Weekly meal plans that adapt to your progress and dietary preferences."
                        icon="📅"
                    />
                    <FeatureCard
                        title="Real-time Coaching"
                        desc="Get instant feedback and suggestions to stay on track with your goals."
                        icon="💪"
                    />
                </div>
            </div>
        </div>
    );
};

const FeatureCard = ({ title, desc, icon }) => (
    <div className="bg-brand-surface/50 border border-white/5 p-8 rounded-2xl hover:bg-brand-surface hover:border-brand-primary/30 transition-all duration-300 group">
        <div className="text-4xl mb-6 bg-brand-dark/50 w-16 h-16 flex items-center justify-center rounded-xl group-hover:scale-110 transition-transform">{icon}</div>
        <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
        <p className="text-gray-400 leading-relaxed">{desc}</p>
    </div>
)

export default Home;
