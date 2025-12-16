from django.urls import path
from django.contrib.auth import views as auth_views
from . import views # We will create this next for Signup

urlpatterns = [
    # Built-in Django Login
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # Built-in Django Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Our Custom Signup
    path('signup/', views.signup, name='signup'),
]