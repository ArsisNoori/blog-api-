from django.urls import path
from . import api_views

urlpatterns = [
    path('register/', api_views.UserRegisterView.as_view(), name='api-register'),
    path('activate/<uidb64>/<token>/', api_views.ActivateAccountView.as_view(), name='api-activate'),
    path('profile/', api_views.UserProfileView.as_view(), name='api-profile'),
]