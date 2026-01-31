import { useState } from 'react';
import { Heart, MessageCircle, Send } from 'lucide-react';
import { likePost, createComment } from '../api';
import Comment from './Comment';

export default function Post({ post, onUpdate, currentUser, onLoginRequired }) {
    const [showCommentForm, setShowCommentForm] = useState(false);
    const [commentContent, setCommentContent] = useState('');
    const [isLiked, setIsLiked] = useState(post.user_has_liked);
    const [likeCount, setLikeCount] = useState(post.like_count);
    const [submitting, setSubmitting] = useState(false);

    const handleLike = async () => {
        if (!currentUser) {
            if (onLoginRequired) onLoginRequired();
            return;
        }
        try {
            const response = await likePost(post.id);
            setIsLiked(response.data.status === 'liked');
            setLikeCount(response.data.like_count);
        } catch (error) {
            console.error('Error liking post:', error);
            if (error.response?.status === 403 || error.response?.status === 401) {
                if (onLoginRequired) onLoginRequired();
            }
        }
    };

    const handleComment = async (e) => {
        e.preventDefault();
        if (!commentContent.trim()) return;

        if (!currentUser) {
            if (onLoginRequired) onLoginRequired();
            return;
        }

        setSubmitting(true);
        try {
            await createComment(post.id, commentContent);
            setCommentContent('');
            setShowCommentForm(false);
            if (onUpdate) onUpdate();
        } catch (error) {
            console.error('Error creating comment:', error);
            if (error.response?.status === 403 || error.response?.status === 401) {
                if (onLoginRequired) onLoginRequired();
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="card animate-slide-up">
            {/* Post Header */}
            <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 
                        flex items-center justify-center font-bold text-lg shadow-lg">
                    {post.author.username[0].toUpperCase()}
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg text-white">{post.author.username}</h3>
                        <span className="px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-300 text-xs">
                            {post.author.total_karma} karma
                        </span>
                    </div>
                    <p className="text-white/60 text-sm">
                        {new Date(post.created_at).toLocaleString()}
                    </p>
                </div>
            </div>

            {/* Post Content */}
            <p className="text-white/90 text-lg leading-relaxed mb-6">{post.content}</p>

            {/* Actions */}
            <div className="flex items-center gap-4 pb-4 border-b border-white/10">
                <button
                    onClick={handleLike}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300
                    ${isLiked
                            ? 'bg-red-500/20 text-red-400 shadow-lg shadow-red-500/20'
                            : 'glass hover:bg-white/20 text-white/60'}`}
                >
                    <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                    <span className="font-semibold">{likeCount}</span>
                </button>

                <button
                    onClick={() => setShowCommentForm(!showCommentForm)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg glass hover:bg-white/20 
                   text-white/60 transition-all duration-300"
                >
                    <MessageCircle className="w-5 h-5" />
                    <span className="font-semibold">{post.comment_count || 0}</span>
                </button>
            </div>

            {/* Comment Form */}
            {showCommentForm && (
                <form onSubmit={handleComment} className="mt-4 animate-slide-up">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={commentContent}
                            onChange={(e) => setCommentContent(e.target.value)}
                            placeholder="Write a comment..."
                            className="input-field flex-1"
                            disabled={submitting}
                            autoFocus
                        />
                        <button
                            type="submit"
                            disabled={submitting || !commentContent.trim()}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </form>
            )}

            {/* Comments */}
            {post.comments && post.comments.length > 0 && (
                <div className="mt-6">
                    <h4 className="text-white/60 text-sm font-semibold mb-4">
                        {post.comments.length} {post.comments.length === 1 ? 'Comment' : 'Comments'}
                    </h4>
                    {post.comments.map((comment) => (
                        <Comment
                            key={comment.id}
                            comment={comment}
                            postId={post.id}
                            onCommentAdded={onUpdate}
                            currentUser={currentUser}
                            onLoginRequired={onLoginRequired}
                            depth={0}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
