from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import dashboard_views as dv
from .views import restaurant_views as rv

app_name = 'restaurants'

urlpatterns = [
    path('create/', dv.create_restaurant, name='create_restaurant'),
    path('dashboard/', dv.dashboard, name='dashboard'),
    path('delete-opening-hour/<int:pk>/', dv.delete_opening_hour, name='delete_opening_hour'),
    path('get_time_choices/', rv.get_time_choices, name='get_time_choices'),
    path('homepage/', rv.user_homepage, name='user_homepage'),
    path('manage-orders/', dv.manage_orders, name='manage_orders'),
    path('manage-orders/order/<int:order_id>/', dv.order_detail, name='order_detail'),
    path('manage-orders/retired/', dv.retired_orders, name='retired_orders'),
    path('delete-reservation/<int:reservation_id>/', dv.delete_reservation, name="owner_delete_reservation"),
    path('menu/add-dish/', dv.add_dish, name='add_dish'),
    path('menu/add-section/', dv.add_section, name='add_section'),
    path('menu/delete-dish/<int:dish_id>/', dv.delete_dish, name='delete_dish'),
    path('menu/modify-dish/<int:dish_id>/', dv.modify_dish, name='modify_dish'),
    path('page/<int:restaurant_id>/', rv.restaurant_page, name='restaurant_page'),
    path('page/<int:restaurant_id>/add-to-order/<int:dish_id>/', rv.add_to_order, name='add_to_order'),
    path('page/<int:restaurant_id>/delete-from-order/<int:item_id>/', rv.delete_from_order, name='delete_from_order'),
    path('page/<int:restaurant_id>/reservation/', rv.make_reservation, name='make_reservation'),
    path('page/<int:restaurant_id>/reservation/<int:reservation_id>/delete/', rv.delete_reservation, name='delete_reservation'),
    path('page/<int:restaurant_id>/submit-order/', rv.submit_order, name='submit_order'),
    path('page/<int:restaurant_id>/delete_order/<int:order_id>/', rv.delete_order, name='delete_order'),
    path('restaurant-list/', rv.restaurant_list, name='restaurant_list'),
    path('reservations/', dv.view_all_reservations, name='all_reservations'),
    path('section/<int:section_id>/delete/', dv.delete_section, name='delete_section'),
    path('section/<int:section_id>/modify/', dv.modify_section, name='modify_section'),
    path('set/address/', dv.set_address, name='set_address'),
    path('set/opening-hours/', dv.set_opening_hours, name='set_opening_hours'),
    path('set/tags/', dv.manage_tags, name='manage_tags'),
    path('set/seats/', dv.set_seats, name='set_seats'),
    path('set/upload_banner/', dv.upload_banner, name='upload_banner'),
    path('set/upload_logo/', dv.upload_logo, name='upload_logo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)