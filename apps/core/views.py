from django.shortcuts import render, get_object_or_404
from apps.properties.models import Property
from django.db.models import Q # <--- Import this for advanced search
from apps.properties.models import Property

#login dashboard
from django.contrib.auth.decorators import login_required
from apps.payments.models import ViewingRequest

def home(request):
    # 1. Start with all available properties
    properties = Property.objects.filter(is_available=True).order_by('-created_at')
    
    # 2. Check if user is searching
    query = request.GET.get('q') # Get the text from the search box
    
    if query:
        # Filter by Title OR Location OR Description
        properties = properties.filter(
            Q(title__icontains=query) | 
            Q(location_area__icontains=query) |
            Q(description__icontains=query)
        )
    
    # 3. Limit to 6 results if just browsing, but show all if searching
    if not query:
        properties = properties[:6]

    context = {
        'properties': properties
    }
    return render(request, 'home.html', context)

def property_detail(request, slug):
    # This function looks for a house with this specific "slug".
    # If it doesn't exist, it shows a 404 Error (Professional handling).
    property = get_object_or_404(Property, slug=slug)
    
    context = {
        'property': property
    }
    return render(request, 'property_detail.html', context)


@login_required # Security: Block non-logged-in users
def dashboard(request):
    # 1. Get properties belonging to this user
    my_properties = request.user.properties.all()
    
    # 2. Get viewing requests (Leads) for these properties
    # We filter for requests where payment was SUCCESSFUL
    my_leads = ViewingRequest.objects.filter(
        property__in=my_properties, 
        has_paid_viewing_fee=True
    ).order_by('-created_at')
    
    context = {
        'properties': my_properties,
        'leads': my_leads
    }
    return render(request, 'dashboard.html', context)