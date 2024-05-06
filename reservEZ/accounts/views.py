# views.py
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_success')  # Redirect to a success page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})
