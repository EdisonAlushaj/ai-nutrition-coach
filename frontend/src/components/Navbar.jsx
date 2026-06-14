import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();

    return (
        <nav className="fixed w-full z-50 bg-brand-dark/80 backdrop-blur-md border-b border-white/10">
            <div className="container mx-auto px-6 py-4 flex justify-between items-center">

                {/* Logo */}
                <Link
                    to="/"
                    className="text-2xl font-bold bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent"
                >
                    AI Coach
                </Link>

                {/* Navigation */}
                <div className="hidden md:flex items-center space-x-8">
                    <Link to="/" className="nav-link">Home</Link>

                    {user && (
                        <>
                            <Link to="/dashboard" className="nav-link">Dashboard</Link>
                            <Link to="/profile" className="nav-link">Profile</Link>
                        </>
                    )}

                    {user?.role === 'admin' && (
                        <Link
                            to="/admin"
                            className="text-brand-accent hover:text-brand-primary font-bold transition-colors"
                        >
                            Admin
                        </Link>
                    )}

                    <div className="h-6 w-px bg-white/20 mx-2"></div>

                    {/* Auth Section */}
                    {user ? (
                        <div className="flex items-center space-x-4">
                            <span className="text-brand-primary text-sm font-medium">
                                Hi, {user.email.split('@')[0]}
                            </span>
                            <button
                                onClick={logout}
                                className="text-gray-300 hover:text-white transition-colors font-medium"
                            >
                                Logout
                            </button>
                        </div>
                    ) : (
                        <>
                            <Link to="/login" className="text-gray-300 hover:text-white font-medium">
                                Login
                            </Link>
                            <Link
                                to="/register"
                                className="bg-gradient-to-r from-brand-primary to-emerald-600 text-white px-6 py-2 rounded-full font-bold shadow-lg transition-all hover:scale-105"
                            >
                                Sign Up
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
