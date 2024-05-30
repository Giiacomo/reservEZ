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
            return redirect('restaurants:create_restaurant')
    return _wrapped_view

def check_restaurant_complete(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = Restaurant.objects.filter(pk=restaurant_id).first()

        if not restaurant:
            return redirect('restaurants:user_homepage')  # Or any other page you prefer

        # Check if all required fields are present
        if not (restaurant.address and restaurant.opening_hours.exists() and restaurant.owner 
                and restaurant.name and restaurant.description):
            return redirect('restaurants:user_homepage')  # Replace 'homepage' with the name of your homepage view

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def filter_complete_restaurants(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        all_restaurants = Restaurant.objects.all()
        complete_restaurants = []

        for restaurant in all_restaurants:
            if (restaurant.address and restaurant.opening_hours.exists() and restaurant.owner 
                and restaurant.name and restaurant.description):
                complete_restaurants.append(restaurant)

        request.complete_restaurants = complete_restaurants
        return view_func(request, *args, **kwargs)
    return _wrapped_view