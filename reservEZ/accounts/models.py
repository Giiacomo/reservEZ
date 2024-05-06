from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(models.Model):
    email = models.EmailField(unique=True)
    cell_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.email
        



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
