# Community Feed - Playto Engineering Challenge

A full-stack community feed application with threaded discussions, gamification, and a dynamic leaderboard.

## 🚀 Features

- **Threaded Comments**: Nested comment system with unlimited depth (Reddit-style)
- **Gamification**: Karma points system (5 points for post likes, 1 point for comment likes)
- **Dynamic Leaderboard**: Top 5 users by karma earned in the last 24 hours
- **Real-time Updates**: Optimistic UI updates for likes and comments
- **Premium UI**: Modern dark theme with glassmorphism effects

## 🛠️ Tech Stack

**Backend:**
- Django 5.1.5
- Django REST Framework 3.15.2
- django-mptt 0.16.0 (for efficient nested comments)
- SQLite (development) / PostgreSQL (production)

**Frontend:**
- React 18 with Vite
- Tailwind CSS
- Axios
- Lucide React (icons)

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- npm or yarn
- Docker & Docker Compose (optional)

## 🏃 Quick Start

### Option 1: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Option 2: Docker

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

## 🧪 Running Tests

```bash
cd backend
python manage.py test community
```

The test suite includes:
- **N+1 Query Prevention Test**: Verifies comment tree loading uses ≤5 queries
- **Concurrency Test**: Ensures no duplicate likes in race conditions
- **24h Leaderboard Test**: Validates dynamic karma calculation
- **Karma Calculation Test**: Confirms correct karma amounts

## 📚 API Endpoints

### Posts
- `GET /api/posts/` - List all posts (paginated)
- `POST /api/posts/` - Create a new post
- `GET /api/posts/{id}/` - Get post with comment tree
- `POST /api/posts/{id}/like/` - Like/unlike a post

### Comments
- `POST /api/comments/` - Create a comment or reply
- `POST /api/comments/{id}/like/` - Like/unlike a comment

### Leaderboard
- `GET /api/leaderboard/` - Get top 5 users by 24h karma

### Users
- `GET /api/users/{id}/` - Get user details

## 🎯 Key Technical Solutions

### 1. N+1 Query Prevention (Comments)
- Uses **django-mptt** for efficient tree structure
- Fetches entire comment tree in 1-2 queries using `prefetch_related`
- See `community/models.py` and `community/serializers.py`

### 2. Concurrency Handling (Likes)
- Database unique constraint on `(user, content_type, object_id)`
- Atomic transactions with `get_or_create()`
- See `community/views.py` like endpoints

### 3. 24-Hour Leaderboard
- Dynamic calculation from `KarmaTransaction` model
- No cached "daily karma" field
- Aggregates transactions from last 24 hours
- See `community/views.py` LeaderboardViewSet

## 📁 Project Structure

```
playto-work/
├── backend/
│   ├── community/          # Main Django app
│   │   ├── models.py       # Database models (MPTT, Like, KarmaTransaction)
│   │   ├── views.py        # API endpoints with concurrency handling
│   │   ├── serializers.py  # DRF serializers with N+1 prevention
│   │   ├── signals.py      # Automatic karma updates
│   │   └── tests.py        # Comprehensive test suite
│   ├── config/             # Django settings
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Feed.jsx    # Main feed
│   │   │   ├── Post.jsx    # Post with likes/comments
│   │   │   ├── Comment.jsx # Recursive comment component
│   │   │   └── Leaderboard.jsx
│   │   ├── api.js          # Axios API client
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yml
├── README.md
└── EXPLAINER.md
```

## 🎨 UI Features

- **Dark Mode**: Premium dark gradient background
- **Glassmorphism**: Frosted glass effects on cards
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first design
- **Leaderboard**: Auto-refreshes every 30 seconds

## 🔐 Authentication

Currently uses Django session authentication. To create posts/comments/likes:

1. Create a superuser: `python manage.py createsuperuser`
2. Login at: `http://localhost:8000/admin`
3. Use the application

## 🚢 Deployment

The application is ready for deployment on platforms like:
- **Railway** (backend + PostgreSQL)
- **Vercel** (frontend)
- **Render** (full-stack)

See `docker-compose.yml` for production configuration.

## 📖 Documentation

See `EXPLAINER.md` for detailed technical explanations of:
- Comment tree database modeling
- Leaderboard SQL/QuerySet
- AI audit and bug fixes

## 👨‍💻 Development

### Adding Sample Data

```bash
cd backend
python manage.py shell
```

```python
from community.models import User, Post, Comment
from django.contrib.contenttypes.models import ContentType

# Create users
user1 = User.objects.create_user('alice', password='pass')
user2 = User.objects.create_user('bob', password='pass')

# Create posts
post = Post.objects.create(author=user1, content='Hello world!')

# Create comments
comment = Comment.objects.create(post=post, author=user2, content='Great post!')
reply = Comment.objects.create(post=post, author=user1, parent=comment, content='Thanks!')
```

## 🐛 Troubleshooting

**CORS errors**: Ensure backend is running on port 8000 and frontend on 5173

**Database locked**: Use PostgreSQL instead of SQLite for concurrent tests

**Import errors**: Ensure all dependencies are installed

## 📝 License

This project is created for the Playto Engineering Challenge.

## 🙏 Acknowledgments

- Django MPTT for efficient tree queries
- Tailwind CSS for rapid UI development
- Lucide React for beautiful icons
