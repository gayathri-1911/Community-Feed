"""
Script to populate the database with sample data for testing.
Run with: python manage.py shell < populate_data.py
"""

from community.models import User, Post, Comment, Like
from django.contrib.contenttypes.models import ContentType

print("Creating sample users...")
users = []
for i in range(5):
    username = f'user{i+1}'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='password123'
        )
        users.append(user)
        print(f"Created {username}")
    else:
        users.append(User.objects.get(username=username))

print("\nCreating sample posts...")
post_contents = [
    "Just discovered this amazing community! 🎉",
    "What's everyone working on today?",
    "Hot take: Nested comments are the best feature of any social platform",
    "Looking for recommendations on Django best practices",
    "The leaderboard system is so motivating! Let's get those karma points! 🚀"
]

posts = []
for i, content in enumerate(post_contents):
    post = Post.objects.create(
        author=users[i % len(users)],
        content=content
    )
    posts.append(post)
    print(f"Created post {i+1}")

print("\nCreating sample comments...")
# Add root comments
for post in posts[:3]:
    for i in range(3):
        Comment.objects.create(
            post=post,
            author=users[(i + 1) % len(users)],
            content=f"Great post! This is comment {i+1}"
        )

# Add nested replies
for post in posts[:2]:
    root_comments = Comment.objects.filter(post=post, parent=None)
    for comment in root_comments[:2]:
        Comment.objects.create(
            post=post,
            author=users[2],
            parent=comment,
            content="I totally agree with this!"
        )
        # Add a third level
        reply = Comment.objects.filter(parent=comment).first()
        if reply:
            Comment.objects.create(
                post=post,
                author=users[3],
                parent=reply,
                content="This is getting deep! 🤔"
            )

print("\nAdding likes...")
# Like some posts
for post in posts[:4]:
    for user in users[:3]:
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=post.id
        )

# Like some comments
comments = Comment.objects.all()[:10]
for comment in comments:
    for user in users[:2]:
        content_type = ContentType.objects.get_for_model(Comment)
        Like.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=comment.id
        )

print("\n✅ Sample data created successfully!")
print(f"Users: {User.objects.count()}")
print(f"Posts: {Post.objects.count()}")
print(f"Comments: {Comment.objects.count()}")
print(f"Likes: {Like.objects.count()}")
print(f"\nYou can now test the application with sample data!")
