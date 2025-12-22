from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Property

# 1. Get your custom user model (accounts.User)
User = get_user_model()

# ==========================
# PROPERTY FORM (For Landlords)
# ==========================
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # ✅ FIXED: Added the missing comma after 'contact_phone'
        fields = ['title', 'contact_phone', 'price', 'location', 'bedrooms', 'bathrooms', 'description', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the fields with Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


# ==========================
# REGISTRATION FORM (For Sign Up)
# ==========================
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the fields with Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'