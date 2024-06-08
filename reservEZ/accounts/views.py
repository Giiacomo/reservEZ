# views.py
from django.shortcuts import render, redirect
from .forms import AddressForm, UserInfoForm, UserRegistrationForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification_count():
    channel_layer = get_channel_layer()
    count = Notification.objects.filter(is_read=False).count()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification_count",
            "count": count
        }
    )

@login_required
def fetch_notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'accounts/partials/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification does not exist'})

# context_processors.py

from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count()
        }
    return {}



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to a success page after registration
    else:
        form = UserRegistrationForm()
    ctx = {
        'title': 'Register',
        'form': form,
    }
    return render(request, 'accounts/registration.html', ctx)

@login_required
def user_dashboard(request):
    user_profile = request.user.profile
    return render(request, 'accounts/dashboard.html', {'user_profile': user_profile})


@login_required
def user_info(request):
    existing_user = request.user
    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=existing_user)
        if form.is_valid():
            form.save()
            return redirect('accounts:info') 
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

            return redirect('accounts:address')  # Redirect to the same page after successful update
    else:
        form = AddressForm(existing_address=existing_address)
    return render(request, 'accounts/user-address.html', {'form': form})

