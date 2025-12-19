from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # ONLY these fields will be validated. 
        # We EXCLUDE 'slug' and 'landlord' because the system handles them.
        fields = ['title', 'price', 'location', 'bedrooms', 'bathrooms', 'description', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the fields with Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'