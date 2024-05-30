from django.urls import path
from .views import user_dashboard, user_info, user_address

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', user_dashboard, name='dashboard'),
    path('dashboard/info/', user_info, name='info'),
    path('dashboard/address/', user_address, name='address')
]
