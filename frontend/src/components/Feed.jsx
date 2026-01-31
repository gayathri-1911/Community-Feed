import { useState, useEffect } from 'react';
import { getPosts, createPost, getCurrentUser, logout as logoutApi, getCsrfToken } from '../api';
import { PlusCircle, Sparkles, LogIn, LogOut, User } from 'lucide-react';
import Post from './Post';
import Leaderboard from './Leaderboard';
import LoginModal from './LoginModal';

export default function Feed() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newPostContent, setNewPostContent] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);

    const fetchPosts = async () => {
        try {
            const response = await getPosts();
            setPosts(response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const checkAuth = async () => {
        try {
            const response = await getCurrentUser();
            if (response.data && response.data.id) {
                setCurrentUser(response.data);
            }
        } catch (error) {
            // Not logged in
        }
    };

    const handleLogout = async () => {
        try {
            await logoutApi();
            setCurrentUser(null);
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const handleLogin = (user) => {
        setCurrentUser(user);
    };

    useEffect(() => {
        // Fetch CSRF token first to set the cookie
        getCsrfToken().then(() => {
            fetchPosts();
            checkAuth();
        }).catch(err => {
            console.error('Error fetching CSRF token:', err);
            // Continue anyway
            fetchPosts();
            checkAuth();
        });
    }, []);

    const handleCreatePost = async (e) => {
        e.preventDefault();
        if (!newPostContent.trim()) return;

        if (!currentUser) {
            setShowLoginModal(true);
            return;
        }

        setSubmitting(true);
        try {
            await createPost(newPostContent);
            setNewPostContent('');
            setShowCreateForm(false);
            await fetchPosts();
        } catch (error) {
            console.error('Error creating post:', error);
            if (error.response?.status === 403 || error.response?.status === 401) {
                setShowLoginModal(true);
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12 animate-fade-in">
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <Sparkles className="w-10 h-10 text-primary-400" />
                        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 
                         bg-clip-text text-transparent">
                            Community Feed
                        </h1>
                        <Sparkles className="w-10 h-10 text-accent-400" />
                    </div>
                    <p className="text-white/60 text-lg">
                        Share your thoughts, engage in discussions, and climb the leaderboard!
                    </p>

                    {/* Auth Status */}
                    <div className="mt-4 flex items-center justify-center gap-3">
                        {currentUser ? (
                            <div className="glass rounded-lg px-4 py-2 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 
                              flex items-center justify-center font-bold text-sm">
                                    {currentUser.username[0].toUpperCase()}
                                </div>
                                <div className="text-left">
                                    <p className="text-white font-semibold">{currentUser.username}</p>
                                    <p className="text-white/60 text-xs">{currentUser.total_karma} karma</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="ml-2 p-2 hover:bg-white/10 rounded-lg transition-colors"
                                    title="Logout"
                                >
                                    <LogOut className="w-4 h-4 text-white/60" />
                                </button>
                            </div>
                        ) : (
                            <button
                                onClick={() => setShowLoginModal(true)}
                                className="glass rounded-lg px-4 py-2 flex items-center gap-2 hover:bg-white/20 transition-colors"
                            >
                                <LogIn className="w-4 h-4" />
                                <span>Login to Post & Like</span>
                            </button>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Feed */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Create Post Button/Form */}
                        {!showCreateForm ? (
                            <button
                                onClick={() => {
                                    if (!currentUser) {
                                        setShowLoginModal(true);
                                    } else {
                                        setShowCreateForm(true);
                                    }
                                }}
                                className="w-full card hover:scale-105 transition-all duration-300 cursor-pointer
                         bg-gradient-to-r from-primary-500/20 to-accent-500/20 border-2 border-primary-500/30"
                            >
                                <div className="flex items-center justify-center gap-3 py-4">
                                    <PlusCircle className="w-6 h-6 text-primary-400" />
                                    <span className="text-lg font-semibold text-white">Create a Post</span>
                                </div>
                            </button>
                        ) : (
                            <div className="card animate-slide-up">
                                <h3 className="text-xl font-bold mb-4 text-white">Create a Post</h3>
                                <form onSubmit={handleCreatePost}>
                                    <textarea
                                        value={newPostContent}
                                        onChange={(e) => setNewPostContent(e.target.value)}
                                        placeholder="What's on your mind?"
                                        className="input-field min-h-[120px] resize-none mb-4"
                                        disabled={submitting}
                                        autoFocus
                                    />
                                    <div className="flex gap-3">
                                        <button
                                            type="submit"
                                            disabled={submitting || !newPostContent.trim()}
                                            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {submitting ? 'Posting...' : 'Post'}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setShowCreateForm(false);
                                                setNewPostContent('');
                                            }}
                                            className="btn-secondary"
                                            disabled={submitting}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            </div>
                        )}

                        {/* Posts */}
                        {loading ? (
                            <div className="space-y-6">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="card animate-pulse">
                                        <div className="h-4 bg-white/20 rounded w-1/4 mb-4"></div>
                                        <div className="h-4 bg-white/20 rounded w-3/4 mb-2"></div>
                                        <div className="h-4 bg-white/20 rounded w-1/2"></div>
                                    </div>
                                ))}
                            </div>
                        ) : posts.length === 0 ? (
                            <div className="card text-center py-12">
                                <Sparkles className="w-16 h-16 mx-auto mb-4 text-white/40" />
                                <h3 className="text-xl font-semibold text-white/60 mb-2">No posts yet</h3>
                                <p className="text-white/40">Be the first to share something!</p>
                            </div>
                        ) : (
                            posts.map((post) => (
                                <Post
                                    key={post.id}
                                    post={post}
                                    onUpdate={fetchPosts}
                                    currentUser={currentUser}
                                    onLoginRequired={() => setShowLoginModal(true)}
                                />
                            ))
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="lg:col-span-1">
                        <Leaderboard />
                    </div>
                </div>
            </div>

            {/* Login Modal */}
            {showLoginModal && (
                <LoginModal
                    onClose={() => setShowLoginModal(false)}
                    onLogin={handleLogin}
                />
            )}
        </div>
    );
}
