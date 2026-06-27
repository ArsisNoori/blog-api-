# posts/api_urls.py

from django.urls import path
from . import api_views

app_name = 'posts_api'

urlpatterns = [
    # Post endpoints
    path('posts/', api_views.PostListCreateView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', api_views.PostDetailView.as_view(), name='post-detail'),
    # Category endpoints
    path('categories/', api_views.CategoryListView.as_view(), name='category-list'),
    path('posts/', api_views.PostListCreateView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', api_views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/comments/', api_views.CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', api_views.CommentDetailView.as_view(), name='comment-detail'),
    path('categories/', api_views.CategoryListView.as_view(), name='category-list'),
    path('posts/<slug:slug>/reaction/', api_views.PostReactionView.as_view(), name='post-reaction'),
    path('comments/<int:pk>/like/', api_views.LikeCommentView.as_view(), name='comment-like'),
]