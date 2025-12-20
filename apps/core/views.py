from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from .models import Property
from .forms import PropertyForm
from apps.payments.models import Payment

# HOMEPAGE
def home(request):
    # Start by getting ALL properties
    properties = Property.objects.all().order_by('-created_at')

    # --- DEBUGGING PRINTS ---
    print("--- SEARCH DEBUG START ---")
    print(f"Incoming GET params: {request.GET}")

    # 1. Check if user sent a LOCATION search
    location_query = request.GET.get('location')
    if location_query:
        location_query = location_query.strip() # Remove spaces (e.g. "Voi " becomes "Voi")
        if location_query: # Check again in case it was just spaces
            print(f"Filtering by Location: {location_query}")
            properties = properties.filter(location__icontains=location_query)

    # 2. Check if user sent a PRICE filter
    price_query = request.GET.get('max_price')
    if price_query:
        price_query = price_query.strip()
        if price_query.isdigit(): # Only filter if it is a valid number
            print(f"Filtering by Max Price: {price_query}")
            properties = properties.filter(price__lte=int(price_query))
        else:
            print("Skipping price filter (invalid number)")

    print(f"Found {properties.count()} properties after filtering.")
    print("--- SEARCH DEBUG END ---")

    context = {
        'properties': properties
    }
    return render(request, 'core/home.html', context)

# PROPERTY DETAIL
def property_detail(request, slug):
    property = Property.objects.get(slug=slug)
    return render(request, 'core/property_detail.html', {'property': property})

# DASHBOARD
@login_required
def dashboard(request):
    # 1. Get all payments made by this specific user
    # order_by('-created_at') means "newest first"
    user_payments = Payment.objects.filter(payer=request.user).order_by('-created_at')
    
    context = {
        'payments': user_payments
    }
    return render(request, 'core/dashboard.html', context)

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