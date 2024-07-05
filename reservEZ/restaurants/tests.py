from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from restaurants.models import Restaurant, OpeningHours, Tag
from accounts.models import Address
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from restaurants.models import Restaurant, OpeningHours, Tag
from accounts.models import Address, UserProfile
from .utils.functions import generate_recommendations
from .models import Reservation, Order  
from datetime import timedelta

class GenerateRecommendationsTestCase(TestCase):
    def setUp(self):
        
        self.tags = [Tag.objects.create(name=f'Tag {i}') for i in range(1, 6)]

        self.complete_restaurants = []
        self.users = []
        
        for i in range(1, 11):
            user = User.objects.create_user(username=f'user{i}', password='password{i}')
            address = Address.objects.create(
                street=f'Street {i}',
                city='Test City' if i <= 8 else 'Other City',
                state='Test State',
                country='Test Country'
            )

            user_profile = user.profile
            user_profile.address = address
            user_profile.save()

            restaurant = Restaurant.objects.create(
                name=f'Restaurant {i}',
                address=address,
                owner=user,
                description=f'Description {i}'
            )
            OpeningHours.objects.create(
                restaurant=restaurant,
                weekday=1,
                opening_time='09:00',
                closing_time='17:00'
            )
            restaurant.tags.add(self.tags[i % 5])

            self.complete_restaurants.append(restaurant)
            self.users.append(user)

        
        self.test_user = self.users[0]
        for i, restaurant in enumerate(self.complete_restaurants[:3], start=1):  
            
            order_date = timezone.now() + timedelta(days=i)
            reservation_date = timezone.now() + timedelta(days=i)

            Order.objects.create(user=self.test_user, restaurant=restaurant, date=order_date)
            Reservation.objects.create(user=self.test_user, restaurant=restaurant, date=reservation_date, time='12:00', number_of_people=i)

    def test_generate_recommendations(self):
        recommendations = generate_recommendations(self.test_user, self.complete_restaurants)
        
        print("Recommendations:", recommendations)  
        
        
        for restaurant in recommendations:
            self.assertIn(restaurant, self.complete_restaurants[:3])


        
        for restaurant in recommendations:
            self.assertEqual(restaurant.address.city, 'Test City')
            user_reservation = self.test_user.reservations.filter(restaurant=restaurant).first()
            if user_reservation and restaurant.tags.exists():  
                self.assertTrue(any(tag in user_reservation.restaurant.tags.all() for tag in restaurant.tags.all()))


        
        recent_restaurant_ids = [restaurant.id for restaurant in self.complete_restaurants[:3]]
        recommended_restaurant_ids = [restaurant.id for restaurant in recommendations]

        
        for id in recent_restaurant_ids:
            self.assertIn(id, recommended_restaurant_ids)
            self.assertLess(recommended_restaurant_ids.index(id), recommended_restaurant_ids.index(id) + 1)





class FilterCompleteRestaurantsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        
        self.complete_restaurant = Restaurant.objects.create(
            name='Complete Restaurant',
            address=Address.objects.create(
                street='Test Street',
                city='Test City',
                state='Test State',
                country='Test Country'
            ),
            owner=self.user,
            description='Test Description'
        )
        OpeningHours.objects.create(
            restaurant=self.complete_restaurant,
            weekday=1, 
            opening_time='09:00',
            closing_time='17:00'
        )
        tag1 = Tag.objects.create(name='Test Tag 1')
        tag2 = Tag.objects.create(name='Test Tag 2')
        self.complete_restaurant.tags.add(tag1, tag2)
        
        
        self.incomplete_restaurant = Restaurant.objects.create(
            name='Incomplete Restaurant',
            address=Address.objects.create(
                street='Another Test Street',
                city='Another Test City',
                state='Another Test State',
                country='Another Test Country'
            ),
            owner=self.user,
            description='Another Test Description'
        )
        self.incomplete_restaurant.tags.add(tag1)

    def test_complete_restaurants_passed_to_view(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('restaurants:user_homepage'))
        
        print(response.context['all_restaurants'])
        
        self.assertTrue(hasattr(response, 'context'))
        self.assertIn(self.complete_restaurant, response.context['all_restaurants'])
        self.assertNotIn(self.incomplete_restaurant, response.context['all_restaurants'])
