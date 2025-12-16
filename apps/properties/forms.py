from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    # We add a manual field for the main image (simple upload)
    image = forms.ImageField(required=True, label="Main Photo")

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'rent_amount', 'deposit_amount',
            'location_area', 'distance_to_highway', 'google_maps_link',
            'property_type', 'water_source', 'has_token_electricity', 'is_tiled',
            'contact_phone'
        ]
        
        # Make it look pretty with Bootstrap classes
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'water_source': forms.Select(attrs={'class': 'form-select'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': '07XX...'}) # Add widget styling for it


        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loop through all fields to add Bootstrap styling
        for field in self.fields:
            if field != 'has_token_electricity' and field != 'is_tiled':
                self.fields[field].widget.attrs.update({'class': 'form-control'})