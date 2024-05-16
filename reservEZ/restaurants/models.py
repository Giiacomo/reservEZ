from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .utils.constants import WEEKDAYS

class OpeningHours(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='opening_hours')
    weekday = models.IntegerField(choices=WEEKDAYS)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        unique_together = ('restaurant', 'weekday')

    def clean(self):
        if self.opening_time >= self.closing_time:
            raise ValidationError("Closing time must be after opening time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(OpeningHours, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_weekday_display()}: {self.opening_time} - {self.closing_time}"

class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    class Meta:
        unique_together = ('street', 'city', 'state', 'country')

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_restaurants')
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='restaurant')

    def save(self, *args, **kwargs):
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
            # If it's a new instance, simply save it
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu')

    def clean(self):
        # Ensure there's only one menu per restaurant
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
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price field

    class Meta:
        unique_together = ('section', 'dname')

    def __str__(self):
        return self.dname
