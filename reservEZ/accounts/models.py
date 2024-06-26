from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

