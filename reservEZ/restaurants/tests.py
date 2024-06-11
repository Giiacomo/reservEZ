from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from restaurants.models import Restaurant, OpeningHours, Tag
from accounts.models import Address

class FilterCompleteRestaurantsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Complete Restaurant
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
        
        # Incomplete Restaurant (missing OpeningHours)
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
