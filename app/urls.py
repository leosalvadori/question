from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Include authentication app URLs (registration, profile, API)
    path('', include('authentication.urls')),
    # Companies and Surveys URLs
    path('', include('companies.urls')),
    path('', include('surveys.urls')),
    path('', include('answers.urls')),

    # Main application URLs
    path('', views.home, name='home'),

    # API Schema & Docs (always enabled)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
