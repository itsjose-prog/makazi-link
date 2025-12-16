from django.shortcuts import render, redirect
from django.contrib.auth import login
# Change the import below to use YOUR new form
from .forms import CustomUserCreationForm 

def signup(request):
    if request.method == 'POST':
        # Use CustomUserCreationForm instead of UserCreationForm
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.is_landlord = True 
            user.save()
            
            login(request, user)
            return redirect('home')
    else:
        # Use CustomUserCreationForm here too
        form = CustomUserCreationForm() 
    
    return render(request, 'accounts/signup.html', {'form': form})