from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, LeaderboardViewSet, UserViewSet
from .auth_views import login_view, logout_view, current_user, get_csrf_token

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('csrf/', get_csrf_token, name='csrf'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', current_user, name='current_user'),
    path('', include(router.urls)),
]
