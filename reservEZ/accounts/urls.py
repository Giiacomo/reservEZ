# urls.py
from django.urls import path
from .views import register_user

app_name = 'accounts'

urlpatterns = [
    path('register/', register_user, name='register_user'),
]
