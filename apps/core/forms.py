from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # Explicitly listed fields only
        fields = ['title', 'image', 'description', 'price', 'location', 'bedrooms', 'bathrooms']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # 🛡️ SAFETY FIX: Make image optional for now to test if that's the blocker
        self.fields['image'].required = False