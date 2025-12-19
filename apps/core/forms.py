from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # We explicitly list ONLY the fields the user fills out.
        # We DO NOT include 'slug' or 'landlord' here, so validation won't fail.
        fields = [
            'title', 
            'image', 
            'description', 
            'price', 
            'location', 
            'bedrooms', 
            'bathrooms'
        ]
        
        # This makes the form look nice with Bootstrap
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Modern Apartment in Voi'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 15000'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mazeras, Kilifi'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }