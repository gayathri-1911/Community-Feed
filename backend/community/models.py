from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """Extended user model with karma tracking."""
    total_karma = models.IntegerField(default=0)
    
    def get_24h_karma(self):
        """Calculate karma earned in the last 24 hours."""
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        karma = KarmaTransaction.objects.filter(
            user=self,
            created_at__gte=twenty_four_hours_ago
        ).aggregate(total=models.Sum('amount'))['total']
        return karma or 0
    
    class Meta:
        db_table = 'users'


class Post(models.Model):
    """Post model for community feed."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:50]}"


class Comment(MPTTModel):
    """
    Nested comment model using MPTT for efficient tree queries.
    This solves the N+1 problem by allowing us to fetch entire comment trees
    in 1-2 queries instead of recursive queries.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    content = models.TextField()
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['created_at']
    
    class Meta:
        db_table = 'comments'
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"


class Like(models.Model):
    """
    Generic Like model that can be applied to Posts or Comments.
    Uses unique constraint to prevent double-liking (concurrency protection).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.content_type} {self.object_id}"


class KarmaTransaction(models.Model):
    """
    Tracks all karma transactions with timestamps.
    This allows dynamic calculation of 24-hour karma without storing it.
    """
    TRANSACTION_TYPES = (
        ('post_like', 'Post Like'),
        ('comment_like', 'Comment Like'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='karma_transactions')
    amount = models.IntegerField()  # +5 for post like, +1 for comment like
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    related_like = models.ForeignKey(Like, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'karma_transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.amount:+d} karma ({self.transaction_type})"
