from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    # AI Analyzer 
    path('ai-analyzer/', views.ai_analyzer, name='ai_analyzer'),
    # Login/Log out Logic
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'), # auth_views.LoginView is a built-in Django view for handling user login. We specify a custom template for the login page.
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # auth_views.LogoutView is a built-in Django view for handling user logout. It doesn't require a template by default, as it simply logs the user out and redirects them.
]