import { useState } from 'react';
import api from '../api';
import { LogIn, X } from 'lucide-react';

export default function LoginModal({ onClose, onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Django session authentication
            const response = await api.post('/login/', { username, password });
            if (response.data.success) {
                onLogin(response.data.user);
                onClose();
            }
        } catch (err) {
            setError('Invalid username or password');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="card max-w-md w-full animate-slide-up">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg">
                            <LogIn className="w-6 h-6 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold">Login</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-200">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                            Username
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="input-field"
                            placeholder="Enter username"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                            placeholder="Enter password"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-3 text-sm">
                        <p className="text-white/80 mb-1">Demo credentials:</p>
                        <p className="text-primary-300 font-mono">Username: admin</p>
                        <p className="text-primary-300 font-mono">Password: admin123</p>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <p className="mt-4 text-center text-white/60 text-sm">
                    You can browse without logging in, but you'll need to login to create posts or like content.
                </p>
            </div>
        </div>
    );
}
