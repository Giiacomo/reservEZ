from django.utils import timezone
from .constants import WEEKDAYS
from django.db.models import Count, Q, Case, When, Value, IntegerField
from ..models import Restaurant, Tag


def generate_recommendations(user):
    # Fetch user's city from the address associated with the user profile
    user_city = user.profile.address.city if user.profile.address else None

    # Get user's favorite tags based on recent orders/reservations
    favorite_tags = Tag.objects.filter(Q(restaurant__orders__user=user) | Q(restaurant__reservations__user=user)) \
                                .annotate(num_interactions=Count('restaurant__orders') + Count('restaurant__reservations')) \
                                .order_by('-num_interactions')[:3]

    # Get recent restaurants where the user ordered or made reservations
    recent_restaurants = Restaurant.objects.filter(Q(orders__user=user) | Q(reservations__user=user)) \
                                            .order_by('-orders__date', '-reservations__date').distinct()[:3]

    # Generate recommendations based on user's city, favorite tags, and recent restaurants
    recommendations = Restaurant.objects.filter(address__city=user_city) \
                                         .filter(tags__in=favorite_tags) \
                                         .annotate(
                                             weight=Case(
                                                 When(id__in=recent_restaurants, then=Value(2)),  # Assign higher weight to recent restaurants
                                                 default=Value(1),  # Assign default weight to other restaurants
                                                 output_field=IntegerField()
                                             )
                                         ) \
                                         .order_by('-weight') \
                                         .distinct()

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




def filter_restaurants(search_query='', selected_city='', selected_tag=''):
    filtered_restaurants = Restaurant.objects.all()

    if search_query:
        filtered_restaurants = filtered_restaurants.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    if selected_city:
        filtered_restaurants = filtered_restaurants.filter(address__city=selected_city)

    if selected_tag:
        filtered_restaurants = filtered_restaurants.filter(tags__id=selected_tag)

    return filtered_restaurants.distinct()