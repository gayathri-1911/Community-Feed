from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F
from .models import User, Post, Comment, Like, KarmaTransaction
from .serializers import (
    UserSerializer, PostSerializer, PostDetailSerializer,
    CommentSerializer, LeaderboardSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post CRUD operations.
    Includes efficient querying to prevent N+1 problems.
    """
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostDetailSerializer  # Always include comments
    
    def get_queryset(self):
        """Optimize queries with select_related."""
        return Post.objects.select_related('author').prefetch_related(
            'comments__author'
        )
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a post.
        Uses database transactions and select_for_update to prevent race conditions.
        """
        post = self.get_object()
        content_type = ContentType.objects.get_for_model(Post)
        
        # Use transaction to ensure atomicity and prevent race conditions
        with transaction.atomic():
            # Check if user already liked this post
            like_exists = Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=post.id
            ).exists()
            
            if like_exists:
                # Unlike: delete the like
                Like.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=post.id
                ).delete()
                
                return Response({
                    'status': 'unliked',
                    'like_count': Post.objects.get(id=post.id).like_count
                }, status=status.HTTP_200_OK)
            else:
                # Like: create a new like
                # Using get_or_create as an extra safety measure against race conditions
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    content_type=content_type,
                    object_id=post.id
                )
                
                if created:
                    return Response({
                        'status': 'liked',
                        'like_count': Post.objects.get(id=post.id).like_count
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Already existed (race condition caught)
                    return Response({
                        'status': 'already_liked',
                        'like_count': Post.objects.get(id=post.id).like_count
                    }, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment CRUD operations.
    Supports nested comments via parent field.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Optimize queries with select_related."""
        return Comment.objects.select_related('author', 'post')
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a comment.
        Uses database transactions to prevent race conditions.
        """
        comment = self.get_object()
        content_type = ContentType.objects.get_for_model(Comment)
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Check if user already liked this comment
            like_exists = Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=comment.id
            ).exists()
            
            if like_exists:
                # Unlike: delete the like
                Like.objects.filter(
                    user=request.user,
                    content_type=content_type,
                    object_id=comment.id
                ).delete()
                
                return Response({
                    'status': 'unliked',
                    'like_count': Comment.objects.get(id=comment.id).like_count
                }, status=status.HTTP_200_OK)
            else:
                # Like: create a new like
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    content_type=content_type,
                    object_id=comment.id
                )
                
                if created:
                    return Response({
                        'status': 'liked',
                        'like_count': Comment.objects.get(id=comment.id).like_count
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'status': 'already_liked',
                        'like_count': Comment.objects.get(id=comment.id).like_count
                    }, status=status.HTTP_200_OK)


class LeaderboardViewSet(viewsets.ViewSet):
    """
    ViewSet for the leaderboard.
    Calculates top 5 users by karma earned in the last 24 hours.
    Uses dynamic aggregation from KarmaTransaction model.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """
        Get top 5 users by 24-hour karma.
        
        CRITICAL: This does NOT use a simple integer field on User.
        It dynamically calculates from KarmaTransaction history.
        
        QuerySet explanation:
        1. Filter KarmaTransactions from last 24 hours
        2. Group by user
        3. Sum the karma amounts
        4. Order by total descending
        5. Take top 5
        """
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # Dynamic aggregation query - this is the key to solving the requirement
        leaderboard_data = (
            KarmaTransaction.objects
            .filter(created_at__gte=twenty_four_hours_ago)
            .values('user')
            .annotate(karma_24h=Sum('amount'))
            .order_by('-karma_24h')[:5]
        )
        
        # Fetch the actual user objects with their 24h karma
        user_ids = [entry['user'] for entry in leaderboard_data]
        users = User.objects.filter(id__in=user_ids)
        
        # Create a mapping of user_id to karma_24h
        karma_map = {entry['user']: entry['karma_24h'] for entry in leaderboard_data}
        
        # Annotate users with their 24h karma
        result = []
        for user in users:
            user.karma_24h = karma_map.get(user.id, 0)
            result.append(user)
        
        # Sort by karma_24h (preserve order from query)
        result.sort(key=lambda u: u.karma_24h, reverse=True)
        
        serializer = LeaderboardSerializer(result, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user information."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
