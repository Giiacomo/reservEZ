from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .utils.constants import WEEKDAYS, STATUS_CHOICES
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import Address
import os, random
from django.conf import settings  
from datetime import datetime

class OpeningHours(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='opening_hours')
    weekday = models.IntegerField(choices=WEEKDAYS)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    available_seats = models.IntegerField(default=0)  

    class Meta:
        unique_together = ('restaurant', 'weekday')

    def update_available_seats(self):
        reservations = Reservation.objects.filter(restaurant=self.restaurant, date__week_day=self.weekday)
        total_reserved_seats = reservations.aggregate(total_seats=Sum('number_of_people'))['total_seats']
        if total_reserved_seats is None:
            total_reserved_seats = 0
        self.available_seats = self.restaurant.max_seats - total_reserved_seats
        self.save()

    def __str__(self):
        return f"{self.get_weekday_display()}: {self.opening_time} - {self.closing_time}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def user_directory_path(instance, filename):
    
    return f'user_{instance.owner.username}/{filename}'

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_restaurants')
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='restaurant')
    tags = models.ManyToManyField(Tag, blank=True)
    banner = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    logo = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    max_seats = models.IntegerField()  

    def get_opening_hours(self):
        return self.opening_hours.all().order_by('weekday')

    def is_open_now(self):
        now = datetime.now().time()
        current_weekday = datetime.now().weekday()
        opening_hours = self.get_opening_hours()
        return any(
            oh.weekday == current_weekday and oh.opening_time <= now < oh.closing_time
            for oh in opening_hours
        )

    def save(self, *args, **kwargs):

        if not self.banner:
            default_banners_path = os.path.join(settings.BASE_DIR, 'media/default/banners')
            if os.path.exists(default_banners_path):
                default_banners = os.listdir(default_banners_path)
                if default_banners:
                    self.banner.name = os.path.join('default/banners', random.choice(default_banners))

            
        if not self.logo:
            default_logos_path = os.path.join(settings.BASE_DIR, 'media/default/logos')
            if os.path.exists(default_logos_path):
                default_logos = os.listdir(default_logos_path)
                if default_logos:
                    self.logo.name = os.path.join('default/logos', random.choice(default_logos))

        if self.pk:
            existing_menu = self.menu.first()
            existing_opening_hours = self.opening_hours.all()

            super().save(*args, **kwargs)

            if existing_menu:
                existing_menu.restaurant = self
                existing_menu.save()
            for opening_hour in existing_opening_hours:
                opening_hour.restaurant = self
                opening_hour.save()
        else:
            
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu')

    def clean(self):
        
        if self.restaurant.menus.exists() and not self.pk:
            raise ValidationError('A restaurant can only have one menu.')

    def __str__(self):
        return "Menu di " + self.restaurant.name

class MenuSection(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='sections')
    sname = models.CharField(max_length=100, blank=False)

    class Meta:
        unique_together = ('menu', 'sname')

    def __str__(self):
        return self.sname

class Dish(models.Model):
    section = models.ForeignKey(MenuSection, on_delete=models.CASCADE, related_name='dishes')
    dname = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    class Meta:
        unique_together = ('section', 'dname')

    def __str__(self):
        return self.dname

class Reservation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date = models.DateField()
    time = models.TimeField()
    number_of_people = models.PositiveIntegerField()

    class Meta:
        unique_together = ('restaurant', 'user', 'date')

    def __str__(self):
        return f"Reservation for {self.user.username} at {self.restaurant.name} on {self.date} at {self.time} for {self.number_of_people} people"

class Order(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='NA')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def is_retired(self):
        return self.status == 'T'

    def __str__(self):
        return f"Order by {self.user.username} at {self.restaurant.name} on {self.date}"

class ActiveOrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='active_items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.dish.dname} in order {self.order}"

@receiver(post_save, sender=ActiveOrderItem)
@receiver(post_delete, sender=ActiveOrderItem)
def update_order_total_price(sender, instance, **kwargs):
    order = instance.order
    order.total_price = sum(item.dish.price * item.quantity for item in order.active_items.all())
    order.save()