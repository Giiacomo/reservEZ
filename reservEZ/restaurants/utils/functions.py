from django.utils import timezone
from .constants import WEEKDAYS

def is_restaurant_open(restaurant):
    current_time = timezone.now().time()
    opening_hours = restaurant.opening_hours.filter(weekday=timezone.now().weekday())
    for hours in opening_hours:
        if hours.opening_time <= current_time <= hours.closing_time:
            return True
    return False


from ..models import Restaurant, Address, OpeningHours

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
    
    return incomplete_fields

