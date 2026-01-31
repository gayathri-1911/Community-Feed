import { useState } from 'react';
import { Heart, MessageCircle, Send } from 'lucide-react';
import { createComment, likeComment } from '../api';

export default function Comment({ comment, postId, onCommentAdded, currentUser, onLoginRequired, depth = 0 }) {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState('');
    const [isLiked, setIsLiked] = useState(comment.user_has_liked);
    const [likeCount, setLikeCount] = useState(comment.like_count);
    const [submitting, setSubmitting] = useState(false);

    const handleLike = async () => {
        if (!currentUser) {
            if (onLoginRequired) onLoginRequired();
            return;
        }
        try {
            const response = await likeComment(comment.id);
            setIsLiked(response.data.status === 'liked');
            setLikeCount(response.data.like_count);
        } catch (error) {
            console.error('Error liking comment:', error);
            if (error.response?.status === 403 || error.response?.status === 401) {
                if (onLoginRequired) onLoginRequired();
            }
        }
    };

    const handleReply = async (e) => {
        e.preventDefault();
        if (!replyContent.trim()) return;

        if (!currentUser) {
            if (onLoginRequired) onLoginRequired();
            return;
        }

        setSubmitting(true);
        try {
            await createComment(postId, replyContent, comment.id);
            setReplyContent('');
            setShowReplyForm(false);
            if (onCommentAdded) onCommentAdded();
        } catch (error) {
            console.error('Error creating reply:', error);
            if (error.response?.status === 403 || error.response?.status === 401) {
                if (onLoginRequired) onLoginRequired();
            }
        } finally {
            setSubmitting(false);
        }
    };

    // Limit nesting depth for UI purposes
    const maxDepth = 5;
    const isMaxDepth = depth >= maxDepth;

    return (
        <div className={`${depth > 0 ? 'ml-8 mt-4' : 'mt-4'} animate-fade-in`}>
            <div className="glass rounded-lg p-4 hover:bg-white/15 transition-all duration-300">
                {/* Comment Header */}
                <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 
                          flex items-center justify-center font-bold text-sm">
                        {comment.author.username[0].toUpperCase()}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-white">{comment.author.username}</span>
                            <span className="text-xs text-white/40">
                                {new Date(comment.created_at).toLocaleDateString()}
                            </span>
                            {depth > 0 && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/60">
                                    Level {depth}
                                </span>
                            )}
                        </div>
                        <p className="text-white/90 leading-relaxed">{comment.content}</p>

                        {/* Actions */}
                        <div className="flex items-center gap-4 mt-3">
                            <button
                                onClick={handleLike}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all duration-300
                          ${isLiked
                                        ? 'bg-red-500/20 text-red-400'
                                        : 'glass hover:bg-white/20 text-white/60'}`}
                            >
                                <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
                                <span className="text-sm font-medium">{likeCount}</span>
                            </button>

                            {!isMaxDepth && (
                                <button
                                    onClick={() => setShowReplyForm(!showReplyForm)}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg glass hover:bg-white/20 
                           text-white/60 transition-all duration-300"
                                >
                                    <MessageCircle className="w-4 h-4" />
                                    <span className="text-sm font-medium">Reply</span>
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Reply Form */}
                {showReplyForm && (
                    <form onSubmit={handleReply} className="mt-4 ml-11 animate-slide-up">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={replyContent}
                                onChange={(e) => setReplyContent(e.target.value)}
                                placeholder="Write a reply..."
                                className="input-field flex-1"
                                disabled={submitting}
                            />
                            <button
                                type="submit"
                                disabled={submitting || !replyContent.trim()}
                                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </form>
                )}
            </div>

            {/* Nested Replies */}
            {comment.children && comment.children.length > 0 && (
                <div className="border-l-2 border-white/10 pl-2">
                    {comment.children.map((child) => (
                        <Comment
                            key={child.id}
                            comment={child}
                            postId={postId}
                            onCommentAdded={onCommentAdded}
                            currentUser={currentUser}
                            onLoginRequired={onLoginRequired}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
