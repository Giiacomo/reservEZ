from django.shortcuts import redirect
from functools import wraps
from restaurants.models import Restaurant
from .functions import get_incomplete_fields

def user_has_restaurant(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user has a restaurant
        if request.user.owned_restaurants.first() is not None:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to restaurant creation page
            return redirect('restaurants:create_restaurant')
    return _wrapped_view

def check_restaurant_complete(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = Restaurant.objects.filter(pk=restaurant_id).first()

        if not restaurant:
            return redirect('restaurants:user_homepage') 

        # Check if all required fields are present
        if get_incomplete_fields(restaurant):
            return redirect('restaurants:user_homepage')  

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def filter_complete_restaurants(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        all_restaurants = Restaurant.objects.all()
        complete_restaurants = []

        for restaurant in all_restaurants:
            if not get_incomplete_fields(restaurant):
                complete_restaurants.append(restaurant)

        request.complete_restaurants = complete_restaurants
        return view_func(request, *args, **kwargs)
    return _wrapped_view