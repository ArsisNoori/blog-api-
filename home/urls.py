from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('detail/<slug:slug>', views.DetailView.as_view(), name='post_detail'),
    path('create/comment/<slug:slug>', views.CreateCommentView.as_view(), name='create_comment'),
    path('update/comment/<int:pk>',views.UpdateCommentView.as_view(),name='update_comment'),
    path('delete/comment/<int:pk>',views.DeleteCommentView.as_view(),name='delete_comment'),
    path('comment/<int:pk>/like/',views.LikeCommentView.as_view(),name='like_comment'),
    path('create/post/', views.CreatePostView.as_view(), name='create_post'),
    path('post/submitted/<slug:slug>/',views.PostSubmittedView.as_view(),name='post_submitted'),
    path('update/post/<slug:slug>',views.UpdatePostView.as_view(),name='update_post'),
    path('delete/post/<slug:slug>',views.DeletePostView.as_view(),name='delete_post'),
    path('post/<slug:slug>/reaction/',views.PostReactionView.as_view(),name='post_reaction'),
    path('manage/posts/',views.ManagePostsView.as_view(),name='manage_posts'),
    path('publish/post/<slug:slug>/',views.PublishPostView.as_view(),name='publish_post'),
    path('unpublish/post/<slug:slug>/',views.RejectPostView.as_view(),name='unpublish_post'),
    path('review/post/<slug:slug>/',views.ReviewPostView.as_view(),name='review_post'),
    path('dashboard/',views.AuthorDashboardView.as_view(),name='author_dashboard'),

]
