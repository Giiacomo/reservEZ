from django.urls import path
from .views.dashboard_views import create_restaurant, upload_logo, upload_banner, manage_tags, dashboard,  manage_orders, order_detail, add_dish, delete_dish, delete_section, modify_dish, delete_dish, add_section, modify_section, delete_section, delete_opening_hour, set_address, set_opening_hours, delete_opening_hour, view_all_reservations, retired_orders
from .views.restaurant_views import restaurant_list, get_time_choices, restaurant_page, delete_from_order, add_to_order, submit_order, make_reservation, delete_reservation, user_homepage

from django.conf import settings
from django.conf.urls.static import static

app_name = 'restaurants' 

urlpatterns = [
    path('set/upload_logo/', upload_logo, name='upload_logo'),
    path('set/upload_banner/', upload_banner, name='upload_banner'),
    path('create/', create_restaurant, name='create_restaurant'),
    path('restaurant-list/', restaurant_list, name='restaurant_list'),
    path('dashboard/', dashboard, name='dashboard'),
    path('menu/delete-dish/<int:dish_id>/', delete_dish, name='delete_dish'),
    path('menu/modify-dish/<int:dish_id>/', modify_dish, name='modify_dish'),
    path('menu/add-dish/', add_dish, name='add_dish'),
    path('menu/add-section/', add_section, name='add_section'),
    path('section/<int:section_id>/modify/', modify_section, name='modify_section'),
    path('section/<int:section_id>/delete/', delete_section, name='delete_section'),
    path('set/address/', set_address, name='set_address'),
    path('set/opening-hours/', set_opening_hours, name='set_opening_hours'),
    path('set/tags/',  manage_tags, name='manage_tags'),
    path('delete-opening-hour/<int:pk>/', delete_opening_hour, name='delete_opening_hour'),
    path('page/<int:restaurant_id>/', restaurant_page, name='restaurant_page'),
    path('page/<int:restaurant_id>/reservation/', make_reservation, name='make_reservation'),
    path('get_time_choices/', get_time_choices, name='get_time_choices'),
    path('page/<int:restaurant_id>/reservation/<int:reservation_id>/delete', delete_reservation, name='delete_reservation'),
    path('page/<int:restaurant_id>/add-to-order/<int:dish_id>/', add_to_order, name='add_to_order'),
    path('page/<int:restaurant_id>/submit-order/', submit_order, name='submit_order'),
    path('page/<int:restaurant_id>/delete-from-order/<int:item_id>/', delete_from_order, name='delete_from_order'),
    path('manage-orders/', manage_orders, name='manage_orders'), 
    path('manage-orders/order/<int:order_id>/', order_detail, name='order_detail'),
    path('manage-orders/retired/', retired_orders, name='retired_orders'),
    path('reservations/', view_all_reservations, name='all_reservations'),
    path('homepage/', user_homepage, name='user_homepage')
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
