from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from .models import Property
from .forms import PropertyForm

# HOMEPAGE
def home(request):
    properties = Property.objects.all()
    return render(request, 'core/home.html', {'properties': properties})

# PROPERTY DETAIL
def property_detail(request, slug):
    property = Property.objects.get(slug=slug)
    return render(request, 'core/property_detail.html', {'property': property})

# DASHBOARD
@login_required
def dashboard(request):
    properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': properties})

# ADD PROPERTY (The problem area)
@login_required
def add_property(request):
    if request.method == 'POST':
        print("📨 SUBMITTING FORM...") # Log 1
        form = PropertyForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ FORM VALID") # Log 2
            property = form.save(commit=False)
            property.landlord = request.user
            property.save() # The model's save() method will handle the slug now
            return redirect('dashboard')
        else:
            print("❌ FORM INVALID") # Log 3
            print(form.errors)       # Log 4 (The detailed error)
    else:
        form = PropertyForm()
    
    return render(request, 'core/add_property.html', {'form': form})

from django.contrib.auth.models import User
from django.http import HttpResponse


def create_admin_user(request):
    User = get_user_model()  # <--- This gets 'accounts.User' automatically
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("✅ SUCCESS: Superuser 'admin' created! <br>Log in with: <b>admin</b> / <b>admin123</b>")
    else:
        return HttpResponse("⚠️ Superuser 'admin' already exists. You can go log in.")