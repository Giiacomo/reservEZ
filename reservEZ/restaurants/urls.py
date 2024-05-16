from django.urls import path
from .views.dashboard_views import create_restaurant, dashboard, add_dish, add_section, set_address, set_opening_hours
from .views.restaurant_views import restaurant_list, restaurant_page, user_homepage

app_name = 'restaurants' 

urlpatterns = [
    path('create/', create_restaurant, name='create_restaurant'),
    path('restaurant-list/', restaurant_list, name='restaurant_list'),
    path('dashboard/', dashboard, name='dashboard'),
    path('menu/add-dish/', add_dish, name='add_dish'),
    path('menu/add-section/', add_section, name='add_section'),
    path('set/address/', set_address, name='set_address'),
    path('set/opening-hours/', set_opening_hours, name='set_opening_hours'),
    path('page/<int:restaurant_id>/', restaurant_page, name='restaurant_page'),
    path('homepage/', user_homepage, name='user_homepage')
]
