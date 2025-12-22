from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .models import Property
from .forms import PropertyForm
from apps.payments.models import Payment
from .forms import PropertyForm, CustomUserCreationForm

# ==========================
# 1. HOME & SEARCH VIEW
# ==========================
def home(request):
    # Start by getting ALL properties (newest first)
    properties = Property.objects.filter(is_approved=True).order_by('-created_at')

    # --- SEARCH LOGIC ---
    # 1. Location Filter
    location_query = request.GET.get('location')
    if location_query:
        location_query = location_query.strip()
        if location_query:
            print(f"🔎 Filtering by Location: {location_query}")
            properties = properties.filter(location__icontains=location_query)

    # 2. Price Filter
    price_query = request.GET.get('max_price')
    if price_query:
        price_query = price_query.strip()
        if price_query.isdigit():
            print(f"💰 Filtering by Max Price: {price_query}")
            properties = properties.filter(price__lte=int(price_query))

    context = {
        'properties': properties
    }
    return render(request, 'core/home.html', context)

# ==========================
# 2. PROPERTY DETAIL VIEW
# ==========================
def property_detail(request, id):
    property = get_object_or_404(Property, id=id)
    
    # 🔒 DEFAULT: NOT PAID
    has_paid = False
    
    # Check if user is logged in first
    if request.user.is_authenticated:
        # Check if they have a COMPLETED payment for THIS property
        has_paid = Payment.objects.filter(
            payer=request.user, 
            property=property, 
            status='COMPLETED'
        ).exists()
    
    context = {
        'property': property,
        'has_paid': has_paid # <--- Pass this "Key" to the template
    }
    return render(request, 'core/property_detail.html', context)

# ==========================
# 3. DASHBOARD VIEW
# ==========================
@login_required
def dashboard(request):
    # 1. Get payments made BY this user (Student View)
    user_payments = Payment.objects.filter(payer=request.user).order_by('-created_at')
    
    # 2. Get properties uploaded BY this user (Landlord View)
    # (Useful if you want to show their listings on the dashboard later)
    user_properties = Property.objects.filter(landlord=request.user).order_by('-created_at')
    
    context = {
        'payments': user_payments,
        'my_properties': user_properties
    }
    return render(request, 'core/dashboard.html', context)

# ==========================
# 4. ADD PROPERTY VIEW
# ==========================
@login_required
def add_property(request):
    if request.method == 'POST':
        print("📨 Submitting Property Form...")
        form = PropertyForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ Form Valid - Saving Property")
            property = form.save(commit=False)
            property.landlord = request.user
            property.save()
            return redirect('dashboard')
        else:
            print("❌ Form Invalid")
            print(form.errors)
    else:
        form = PropertyForm()
    
    return render(request, 'core/add_property.html', {'form': form})

# ==========================
# 5. UTILITY: CREATE ADMIN
# ==========================
def create_admin_user(request):
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("✅ SUCCESS: Superuser 'admin' created! <br>Log in with: <b>admin</b> / <b>admin123</b>")
    else:
        return HttpResponse("⚠️ Superuser 'admin' already exists. You can go log in.")
    
    # ==========================
# 6. REGISTER VIEW
# ==========================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after signing up
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm() 
    
    return render(request, 'registration/register.html', {'form': form})