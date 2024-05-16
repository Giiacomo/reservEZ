from django.shortcuts import render, get_object_or_404
from ..models import Restaurant, MenuSection
from accounts.models import UserProfile

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant-list.html', {'restaurants': restaurants, 'title': 'List of restaurants:'})

def restaurant_page(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_sections = MenuSection.objects.filter(menu__restaurant=restaurant)

    context = {
        'restaurant': restaurant,
        'menu_sections': menu_sections,
    }
    return render(request, 'restaurants/restaurant-page.html', context)


def user_homepage(request):
    # Fetch user profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Get user's city from the address associated with the user profile
    user_city = user_profile.address.city if user_profile.address else None

    # Fetch all restaurants
    all_restaurants = Restaurant.objects.all()

    # Sort restaurants based on whether they match user's city or not
    user_city_restaurants = all_restaurants.filter(address__city=user_city)
    other_restaurants = all_restaurants.exclude(address__city=user_city)

    if request.method == 'GET':
        query = request.GET.get('q')
        if query:
            # Search restaurants by name or description
            user_city_restaurants = user_city_restaurants.filter(name__icontains=query) | user_city_restaurants.filter(description__icontains=query)
            other_restaurants = other_restaurants.filter(name__icontains=query) | other_restaurants.filter(description__icontains=query)

    context = {
        'user_city_restaurants': user_city_restaurants,
        'other_restaurants': other_restaurants,
    }
    return render(request, 'restaurants/homepage.html', context)