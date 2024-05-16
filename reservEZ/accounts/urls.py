from django.urls import path
from .views import profile, user_info, user_address

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('user-info/', user_info, name='user_info'),
    path('user-address/', user_address, name='user_address')
]
