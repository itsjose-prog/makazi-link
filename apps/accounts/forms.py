from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User # <--- This tells Django to use OUR custom user
        fields = ('username', 'email') # Add fields you want on the signup page