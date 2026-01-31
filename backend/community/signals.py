from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Like, KarmaTransaction, Post, Comment


@receiver(post_save, sender=Like)
def create_karma_transaction(sender, instance, created, **kwargs):
    """
    Create a karma transaction when a like is created.
    Post likes = 5 karma, Comment likes = 1 karma.
    """
    if created:
        # Determine the amount based on what was liked
        content_type = instance.content_type
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        if content_type == post_ct:
            amount = 5
            transaction_type = 'post_like'
            # Get the post and its author
            post = Post.objects.get(id=instance.object_id)
            recipient = post.author
        elif content_type == comment_ct:
            amount = 1
            transaction_type = 'comment_like'
            # Get the comment and its author
            comment = Comment.objects.get(id=instance.object_id)
            recipient = comment.author
        else:
            return
        
        # Create karma transaction for the content author (not the liker)
        KarmaTransaction.objects.create(
            user=recipient,
            amount=amount,
            transaction_type=transaction_type,
            related_like=instance
        )
        
        # Update cached total karma
        recipient.total_karma += amount
        recipient.save(update_fields=['total_karma'])


@receiver(post_delete, sender=Like)
def delete_karma_transaction(sender, instance, **kwargs):
    """
    Remove karma transaction when a like is deleted (unlike).
    """
    # Delete the related karma transaction
    karma_transactions = KarmaTransaction.objects.filter(related_like=instance)
    
    for transaction in karma_transactions:
        # Update cached total karma
        user = transaction.user
        user.total_karma -= transaction.amount
        user.save(update_fields=['total_karma'])
        
        # Delete the transaction
        transaction.delete()


@receiver(post_save, sender=Like)
def update_like_count_on_create(sender, instance, created, **kwargs):
    """Update cached like_count when a like is created."""
    if created:
        content_type = instance.content_type
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        if content_type == post_ct:
            post = Post.objects.get(id=instance.object_id)
            post.like_count += 1
            post.save(update_fields=['like_count'])
        elif content_type == comment_ct:
            comment = Comment.objects.get(id=instance.object_id)
            comment.like_count += 1
            comment.save(update_fields=['like_count'])


@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance, **kwargs):
    """Update cached like_count when a like is deleted."""
    content_type = instance.content_type
    post_ct = ContentType.objects.get_for_model(Post)
    comment_ct = ContentType.objects.get_for_model(Comment)
    
    if content_type == post_ct:
        try:
            post = Post.objects.get(id=instance.object_id)
            post.like_count = max(0, post.like_count - 1)
            post.save(update_fields=['like_count'])
        except Post.DoesNotExist:
            pass
    elif content_type == comment_ct:
        try:
            comment = Comment.objects.get(id=instance.object_id)
            comment.like_count = max(0, comment.like_count - 1)
            comment.save(update_fields=['like_count'])
        except Comment.DoesNotExist:
            pass
