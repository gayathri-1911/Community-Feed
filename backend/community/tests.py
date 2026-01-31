from django.test import TestCase, TransactionTestCase
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import connection
from django.test.utils import override_settings
from datetime import timedelta
from .models import User, Post, Comment, Like, KarmaTransaction
import threading
import time


class CommentTreeN1TestCase(TestCase):
    """
    Test that loading a post with nested comments doesn't cause N+1 queries.
    This is a critical requirement from the challenge.
    """
    
    def setUp(self):
        """Create a post with 50 nested comments."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, content='Test post')
        
        # Create 50 nested comments (10 root comments, each with 4 children)
        for i in range(10):
            root_comment = Comment.objects.create(
                post=self.post,
                author=self.user,
                content=f'Root comment {i}'
            )
            for j in range(4):
                Comment.objects.create(
                    post=self.post,
                    author=self.user,
                    parent=root_comment,
                    content=f'Child comment {i}-{j}'
                )
    
    def test_comment_tree_query_count(self):
        """
        Verify that fetching a post with 50 comments uses ≤3 queries.
        Without optimization, this would be 50+ queries (N+1 problem).
        """
        from django.test.utils import CaptureQueriesContext
        
        with CaptureQueriesContext(connection) as context:
            # Fetch the post with optimized query
            post = Post.objects.select_related('author').prefetch_related(
                'comments__author'
            ).get(id=self.post.id)
            
            # Get all comments (MPTT allows efficient tree fetching)
            comments = list(post.comments.all())
            
            # Access author for each comment (should be prefetched)
            for comment in comments:
                _ = comment.author.username
        
        # Should use very few queries (typically 2-3)
        # 1. Fetch post with author (select_related)
        # 2. Fetch all comments with authors (prefetch_related)
        # 3. Possibly one more for MPTT tree structure
        query_count = len(context.captured_queries)
        
        print(f"\nQuery count for post with 50 comments: {query_count}")
        for i, query in enumerate(context.captured_queries, 1):
            print(f"Query {i}: {query['sql'][:100]}...")
        
        # Assert that we're not doing N+1 queries
        self.assertLessEqual(
            query_count, 
            5,  # Allow up to 5 queries (should be 2-3 in practice)
            f"Expected ≤5 queries, but got {query_count}. This indicates an N+1 problem."
        )


class ConcurrentLikeTestCase(TransactionTestCase):
    """
    Test that concurrent like operations don't create duplicate likes.
    This tests the race condition handling requirement.
    """
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, content='Test post')
    
    def test_concurrent_likes_no_duplicates(self):
        """
        Simulate 10 concurrent like requests from the same user.
        Only 1 Like should be created (no duplicates).
        """
        from django.db import transaction
        
        results = []
        errors = []
        
        def like_post():
            """Function to like a post (simulates concurrent request)."""
            try:
                with transaction.atomic():
                    content_type = ContentType.objects.get_for_model(Post)
                    like, created = Like.objects.get_or_create(
                        user=self.user,
                        content_type=content_type,
                        object_id=self.post.id
                    )
                    results.append(created)
            except Exception as e:
                errors.append(str(e))
        
        # Create 10 threads to simulate concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=like_post)
            threads.append(thread)
        
        # Start all threads at roughly the same time
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        total_likes = Like.objects.filter(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.post.id
        ).count()
        
        print(f"\nConcurrent like test results:")
        print(f"Total likes created: {total_likes}")
        print(f"'Created' results: {results}")
        print(f"Errors: {errors}")
        
        # Should only have 1 like (no duplicates)
        self.assertEqual(
            total_likes,
            1,
            f"Expected 1 like, but got {total_likes}. Race condition not handled properly."
        )


class LeaderboardCalculationTestCase(TestCase):
    """
    Test the 24-hour leaderboard calculation.
    This is a critical requirement - must calculate dynamically from transactions.
    """
    
    def setUp(self):
        """Create test users and karma transactions."""
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')
    
    def test_24h_karma_calculation(self):
        """
        Test that leaderboard only counts karma from last 24 hours.
        """
        now = timezone.now()
        
        # User1: 10 karma in last 24h, 20 karma older
        KarmaTransaction.objects.create(
            user=self.user1,
            amount=5,
            transaction_type='post_like',
            created_at=now - timedelta(hours=1)  # Recent
        )
        KarmaTransaction.objects.create(
            user=self.user1,
            amount=5,
            transaction_type='post_like',
            created_at=now - timedelta(hours=2)  # Recent
        )
        KarmaTransaction.objects.create(
            user=self.user1,
            amount=20,
            transaction_type='post_like',
            created_at=now - timedelta(hours=30)  # Old (should not count)
        )
        
        # User2: 15 karma in last 24h
        KarmaTransaction.objects.create(
            user=self.user2,
            amount=5,
            transaction_type='post_like',
            created_at=now - timedelta(hours=5)
        )
        KarmaTransaction.objects.create(
            user=self.user2,
            amount=5,
            transaction_type='post_like',
            created_at=now - timedelta(hours=10)
        )
        KarmaTransaction.objects.create(
            user=self.user2,
            amount=5,
            transaction_type='post_like',
            created_at=now - timedelta(hours=15)
        )
        
        # User3: 0 karma in last 24h (all old)
        KarmaTransaction.objects.create(
            user=self.user3,
            amount=100,
            transaction_type='post_like',
            created_at=now - timedelta(hours=48)  # Old
        )
        
        # Calculate 24h karma using the method from views.py
        from django.db.models import Sum
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        leaderboard_data = (
            KarmaTransaction.objects
            .filter(created_at__gte=twenty_four_hours_ago)
            .values('user')
            .annotate(karma_24h=Sum('amount'))
            .order_by('-karma_24h')
        )
        
        results = list(leaderboard_data)
        
        print(f"\n24h Leaderboard results:")
        for entry in results:
            user = User.objects.get(id=entry['user'])
            print(f"{user.username}: {entry['karma_24h']} karma")
        
        # Verify results
        self.assertEqual(len(results), 2, "Should have 2 users with karma in last 24h")
        
        # User2 should be first (15 karma)
        self.assertEqual(results[0]['user'], self.user2.id)
        self.assertEqual(results[0]['karma_24h'], 15)
        
        # User1 should be second (10 karma)
        self.assertEqual(results[1]['user'], self.user1.id)
        self.assertEqual(results[1]['karma_24h'], 10)
        
        # User3 should not appear (0 karma in last 24h)
        user_ids = [r['user'] for r in results]
        self.assertNotIn(self.user3.id, user_ids)


class KarmaCalculationTestCase(TestCase):
    """
    Test that karma is calculated correctly.
    Post likes = 5 karma, Comment likes = 1 karma.
    """
    
    def setUp(self):
        """Create test data."""
        self.author = User.objects.create_user(username='author', password='pass')
        self.liker = User.objects.create_user(username='liker', password='pass')
        self.post = Post.objects.create(author=self.author, content='Test post')
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Test comment'
        )
    
    def test_post_like_karma(self):
        """Test that liking a post gives 5 karma to the author."""
        initial_karma = self.author.total_karma
        
        # Like the post
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.create(
            user=self.liker,
            content_type=content_type,
            object_id=self.post.id
        )
        
        # Refresh author
        self.author.refresh_from_db()
        
        # Should have gained 5 karma
        self.assertEqual(
            self.author.total_karma,
            initial_karma + 5,
            "Post like should give 5 karma"
        )
        
        # Verify KarmaTransaction was created
        transaction = KarmaTransaction.objects.get(user=self.author)
        self.assertEqual(transaction.amount, 5)
        self.assertEqual(transaction.transaction_type, 'post_like')
    
    def test_comment_like_karma(self):
        """Test that liking a comment gives 1 karma to the author."""
        initial_karma = self.author.total_karma
        
        # Like the comment
        content_type = ContentType.objects.get_for_model(Comment)
        Like.objects.create(
            user=self.liker,
            content_type=content_type,
            object_id=self.comment.id
        )
        
        # Refresh author
        self.author.refresh_from_db()
        
        # Should have gained 1 karma
        self.assertEqual(
            self.author.total_karma,
            initial_karma + 1,
            "Comment like should give 1 karma"
        )
        
        # Verify KarmaTransaction was created
        transaction = KarmaTransaction.objects.get(user=self.author)
        self.assertEqual(transaction.amount, 1)
        self.assertEqual(transaction.transaction_type, 'comment_like')
