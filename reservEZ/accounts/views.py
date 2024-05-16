# views.py
from django.shortcuts import render, redirect
from .forms import AddressForm, UserInfoForm, UserRegistrationForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')  # Redirect to a success page after registration
    else:
        form = UserRegistrationForm()
    ctx = {
        'title': 'Register',
        'form': form,
    }
    return render(request, 'accounts/registration.html', ctx)

@login_required
def profile(req):
    return render(req, 'accounts/profile.html')

@login_required
def user_info(request):
    existing_user = request.user
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=existing_user)
        if form.is_valid():
            form.save()
            return redirect('user_info') 
    else:
        form = UserInfoForm(instance=existing_user)
    return render(request, 'accounts/user-info.html', {'form': form})

@login_required
def user_address(request):
    user_profile = request.user.profile
    existing_address = user_profile.address
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=existing_address)
        if form.is_valid():
            address_instance = form.save(commit=False)  # Save the form but don't commit to database yet
            address_instance.save()  # Save the address instance

            # Update the user profile with the new address
            user_profile.address = address_instance
            user_profile.save()

            return redirect('user_address')  # Redirect to the same page after successful update
    else:
        form = AddressForm(existing_address=existing_address)
    return render(request, 'accounts/user-address.html', {'form': form})