from django.utils import timezone
from .constants import WEEKDAYS
from django.db.models import Count, Q, Case, When, Value, IntegerField
from ..models import Restaurant, Tag


def generate_recommendations(user, complete_restaurants):
    # Fetch user's city from the address associated with the user profile
    user_city = user.profile.address.city if user.profile.address else None

    # Get user's favorite tags based on recent orders/reservations
    favorite_tags = Tag.objects.filter(
        Q(restaurant__orders__user=user) | Q(restaurant__reservations__user=user)
    ).annotate(
        num_interactions=Count('restaurant__orders') + Count('restaurant__reservations')
    ).order_by(
        '-num_interactions'
    )[:3]
    favorite_tag_ids = [tag.id for tag in favorite_tags]

    # Get recent restaurants where the user ordered or made reservations
    recent_restaurants = Restaurant.objects.filter(
        Q(orders__user=user) | Q(reservations__user=user)
    ).order_by(
        '-orders__date', '-reservations__date'
    ).distinct()[:3]
    recent_restaurant_ids = [restaurant.id for restaurant in recent_restaurants]

    # Filter the complete restaurants based on the user's city
    filtered_restaurants = [
        restaurant for restaurant in complete_restaurants 
        if restaurant.address.city == user_city
    ]

    # Further filter the complete restaurants based on favorite tags
    filtered_restaurants = [
        restaurant for restaurant in filtered_restaurants 
        if any(tag.id in favorite_tag_ids for tag in restaurant.tags.all())
    ]

    # Annotate and sort the filtered restaurants based on recent interactions
    for restaurant in filtered_restaurants:
        restaurant.weight = 2 if restaurant.id in recent_restaurant_ids else 1
    
    recommendations = sorted(filtered_restaurants, key=lambda r: r.weight, reverse=True)

    return recommendations


def is_restaurant_open(restaurant):
    current_time = timezone.now().time()
    opening_hours = restaurant.opening_hours.filter(weekday=timezone.now().weekday())
    for hours in opening_hours:
        if hours.opening_time <= current_time <= hours.closing_time:
            return True
    return False

def get_incomplete_fields(restaurant):
    incomplete_fields = []

    if not restaurant.address:
        incomplete_fields.append('Address')
    elif not all([restaurant.address.street, restaurant.address.city, restaurant.address.state, restaurant.address.country]):
        incomplete_fields.append('Complete Address Details')

    if not restaurant.opening_hours.exists():
        incomplete_fields.append('Opening Hours')

    if not restaurant.owner:
        incomplete_fields.append('Owner')
    
    if not restaurant.name:
        incomplete_fields.append('Name')
    
    if not restaurant.description:
        incomplete_fields.append('Description')
    
    if restaurant.tags.count() == 0:
        incomplete_fields.append('Tags')
    
    return incomplete_fields




def filter_restaurants(search_query='', selected_city='', selected_tag='', filtered_restaurants=None):

    if search_query:
        filtered_restaurants = filtered_restaurants.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    if selected_city:
        filtered_restaurants = filtered_restaurants.filter(address__city=selected_city)

    if selected_tag:
        filtered_restaurants = filtered_restaurants.filter(tags__id=selected_tag)

    return filtered_restaurants