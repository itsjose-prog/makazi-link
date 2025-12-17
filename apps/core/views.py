from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Property
from .forms import PropertyForm

# --- 1. HOMEPAGE VIEW ---
def home(request):
    # This fetches all properties from the database (newest first)
    properties = Property.objects.all().order_by('-created_at')
    # It sends the list to your HTML
    return render(request, 'core/home.html', {'properties': properties})

# --- 2. PROPERTY DETAIL VIEW ---
def property_detail(request, slug):
    property_obj = get_object_or_404(Property, slug=slug)
    return render(request, 'core/property_detail.html', {'property': property_obj})

# --- 3. DASHBOARD VIEW ---
@login_required
def dashboard(request):
    # Fetch only the properties created by the current user
    my_properties = Property.objects.filter(landlord=request.user).order_by('-created_at')
    
    return render(request, 'core/dashboard.html', {'properties': my_properties})

# --- 4. ADD PROPERTY VIEW ---
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.landlord = request.user
            property_obj.save()
            return redirect('dashboard')
    else:
        form = PropertyForm()
    
    return render(request, 'core/add_property.html', {'form': form})