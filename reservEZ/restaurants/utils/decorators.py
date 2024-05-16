from django.shortcuts import redirect
from functools import wraps
from restaurants.models import Restaurant

def user_has_restaurant(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user has a restaurant
        if request.user.owned_restaurants.first() is not None:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to restaurant creation page
            return redirect('create_restaurant')
    return _wrapped_view
