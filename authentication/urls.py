from django.urls import path
from . import views

# Web URLs for user registration and profile management
urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]
