import os
import django
from django.contrib.auth.models import User
from accounts.models import Address, UserProfile
from restaurants.models import Restaurant, Tag, Menu, MenuSection, Dish, OpeningHours
from restaurants.utils.constants import TAG_CHOICES
from datetime import time
from django.core.management import call_command


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservez.settings')
django.setup()

def flush_database():
    call_command('flush', '--no-input')
    call_command('migrate')

def create_users_and_restaurants():
    
    user_addresses = [
        Address.objects.create(street=f'Via Utente {i}', city=f'Città {i}', state=f'Stato {i}', country='Italia', postal_code=f'000{i:02d}') for i in range(20)
    ]
    restaurant_addresses = [
        Address.objects.create(street=f'Via Ristorante {i}', city='Modena' if i < 10 else f'Città {i}', state='MO' if i < 10 else f'Stato {i}', country='Italia', postal_code=f'4112{i:02d}' if i < 10 else f'100{i:02d}') for i in range(15)
    ]

    
    users = []
    for i in range(20):
        user = User.objects.create_user(username=f'user{i}', email=f'user{i}@example.com', password='password123')
        users.append(user)
        user.profile.address = user_addresses[i]  
        user.profile.save()

    
    tag_objects = {tag[0]: Tag.objects.create(name=tag[1]) for tag in TAG_CHOICES}

    
    restaurants = []
    for i in range(15):
        restaurant = Restaurant.objects.create(
            owner=users[i],
            name=f'Ristorante {i}',
            description=f'Descrizione del Ristorante {i}',
            address=restaurant_addresses[i],
            max_seats=100
        )
        
        restaurant.tags.add(tag_objects['pizza'], tag_objects['pasta'])  
        restaurants.append(restaurant)

    
    for restaurant in restaurants:
        menu = Menu.objects.create(restaurant=restaurant)
        section = MenuSection.objects.create(menu=menu, sname='Antipasti')
        Dish.objects.create(section=section, dname='Bruschetta', description='Pane tostato con pomodoro', price=5.00)
        section = MenuSection.objects.create(menu=menu, sname='Primi Piatti')
        Dish.objects.create(section=section, dname='Spaghetti alla Carbonara', description='Spaghetti con uova, pancetta e pecorino', price=10.00)

    
    for restaurant in restaurants:
        for weekday in range(7):
            OpeningHours.objects.create(
                restaurant=restaurant,
                weekday=weekday,
                opening_time=time(12, 0),
                closing_time=time(23, 0),
                available_seats=100
            )


flush_database()
create_users_and_restaurants()