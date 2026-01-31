from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import User, Post, Comment, Like, KarmaTransaction


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""
    karma_24h = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'total_karma', 'karma_24h']
        read_only_fields = ['total_karma', 'karma_24h']
    
    def get_karma_24h(self, obj):
        """Get karma earned in last 24 hours."""
        return obj.get_24h_karma()


class RecursiveCommentSerializer(serializers.ModelSerializer):
    """
    Recursive serializer for nested comments.
    Uses MPTT's get_cached_trees() to avoid N+1 queries.
    """
    author = UserSerializer(read_only=True)
    children = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'like_count', 'created_at', 
                  'updated_at', 'level', 'children', 'user_has_liked']
        read_only_fields = ['like_count', 'created_at', 'updated_at', 'level']
    
    def get_children(self, obj):
        """Recursively serialize children comments."""
        # MPTT caches the tree structure, so this doesn't cause N+1 queries
        if hasattr(obj, 'get_cached_children'):
            children = obj.get_cached_children()
        else:
            children = obj.get_children()
        
        # Limit depth to prevent excessive nesting
        if obj.level < 10:  # Max 10 levels deep
            return RecursiveCommentSerializer(children, many=True, context=self.context).data
        return []
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    author = UserSerializer(read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'author', 'content', 'like_count', 
                  'created_at', 'updated_at', 'user_has_liked']
        read_only_fields = ['author', 'like_count', 'created_at', 'updated_at']
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts."""
    author = UserSerializer(read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'like_count', 'comment_count',
                  'created_at', 'updated_at', 'user_has_liked']
        read_only_fields = ['author', 'like_count', 'created_at', 'updated_at']
    
    def get_user_has_liked(self, obj):
        """Check if current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Post)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False
    
    def get_comment_count(self, obj):
        """Get total comment count for this post."""
        return obj.comments.count()


class PostDetailSerializer(PostSerializer):
    """Detailed post serializer with comment tree."""
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        """
        Get all comments in a tree structure.
        Uses MPTT's get_cached_trees() to fetch entire tree in 1-2 queries.
        """
        # Get root comments (no parent) with their descendants cached
        root_comments = obj.comments.filter(parent=None).prefetch_related('author')
        
        # Use MPTT to cache the entire tree structure
        from mptt.templatetags.mptt_tags import cache_tree_children
        root_comments = cache_tree_children(root_comments)
        
        return RecursiveCommentSerializer(root_comments, many=True, context=self.context).data


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard with 24h karma."""
    karma_24h = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'karma_24h', 'total_karma']
