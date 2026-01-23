const Footer = () => {
    return (
        <footer className="bg-brand-surface border-t border-white/5 text-gray-400 py-8 mt-auto">
            <div className="container mx-auto px-6 text-center">
                <p className="mb-4">&copy; {new Date().getFullYear()} AI Nutrition Coach. Fueling your potential.</p>
                <div className="flex justify-center space-x-6 text-sm">
                    <a href="#" className="hover:text-brand-primary transition-colors">Privacy Policy</a>
                    <a href="#" className="hover:text-brand-primary transition-colors">Terms of Service</a>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
