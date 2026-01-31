import { useState, useEffect } from 'react';
import { getLeaderboard } from '../api';
import { Trophy, TrendingUp } from 'lucide-react';

export default function Leaderboard() {
    const [leaders, setLeaders] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchLeaderboard = async () => {
        try {
            const response = await getLeaderboard();
            setLeaders(response.data);
        } catch (error) {
            console.error('Error fetching leaderboard:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLeaderboard();
        // Refresh every 30 seconds
        const interval = setInterval(fetchLeaderboard, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="card sticky top-4">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg">
                    <Trophy className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold">Leaderboard</h2>
                    <p className="text-white/60 text-sm">Top 5 • Last 24 hours</p>
                </div>
            </div>

            {loading ? (
                <div className="space-y-3">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="glass rounded-lg p-4 animate-pulse">
                            <div className="h-4 bg-white/20 rounded w-3/4"></div>
                        </div>
                    ))}
                </div>
            ) : leaders.length === 0 ? (
                <div className="text-center py-8 text-white/60">
                    <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No karma earned yet!</p>
                    <p className="text-sm mt-1">Be the first to get likes</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {leaders.map((leader, index) => (
                        <div
                            key={leader.id}
                            className="glass rounded-lg p-4 hover:bg-white/20 transition-all duration-300 
                         hover:scale-105 cursor-pointer group"
                        >
                            <div className="flex items-center gap-4">
                                <div
                                    className={`
                    flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg
                    ${index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white' : ''}
                    ${index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-white' : ''}
                    ${index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' : ''}
                    ${index > 2 ? 'bg-white/10 text-white/60' : ''}
                  `}
                                >
                                    {index + 1}
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-white group-hover:text-primary-300 transition-colors">
                                        {leader.username}
                                    </p>
                                    <p className="text-sm text-white/60">
                                        Total: {leader.total_karma} karma
                                    </p>
                                </div>
                                <div className="text-right">
                                    <p className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 
                               bg-clip-text text-transparent">
                                        {leader.karma_24h}
                                    </p>
                                    <p className="text-xs text-white/60">24h karma</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="mt-6 pt-4 border-t border-white/10">
                <p className="text-xs text-white/40 text-center">
                    Post likes: <span className="text-primary-400 font-semibold">+5 karma</span>
                    {' • '}
                    Comment likes: <span className="text-accent-400 font-semibold">+1 karma</span>
                </p>
            </div>
        </div>
    );
}
