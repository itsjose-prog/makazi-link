
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PropertyForm
from .models import PropertyImage
from .models import Property
from django.core.paginator import Paginator # Optional: for later if you have 100s of houses


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES) # Note request.FILES for images
        if form.is_valid():
            # 1. Save the Property info (but don't commit to DB yet)
            property_obj = form.save(commit=False)
            
            # 2. Auto-assign the logged-in user as the Landlord
            property_obj.landlord = request.user
            property_obj.save()
            
            # 3. Handle the Image separately
            image = request.FILES.get('image')
            if image:
                PropertyImage.objects.create(property=property_obj, image=image, is_feature=True)
            
            messages.success(request, "Property listed successfully!")
            return redirect('dashboard')
    else:
        form = PropertyForm()

    return render(request, 'properties/add_property.html', {'form': form})

def all_properties(request):
    # Get all active properties, newest first
    properties_list = Property.objects.filter(is_available=True).order_by('-created_at')
    
    context = {
        'properties': properties_list
    }
    return render(request, 'properties/all_properties.html', context)
