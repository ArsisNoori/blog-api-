from django.urls import path
from . import views
from django.contrib.auth import views  as auth_views
app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
path(
    'activate/<uidb64>/<token>/',
    views.ActivateAccountView.as_view(),
    name='activate'
),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='user_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='user_logout'),

]