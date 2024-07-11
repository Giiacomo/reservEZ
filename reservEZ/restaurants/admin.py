from django.contrib import admin
from .models import OpeningHours, Tag, Restaurant, Menu, MenuSection, Dish, Reservation, Order, ActiveOrderItem


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'get_weekday_display', 'opening_time', 'closing_time', 'available_seats')
    list_filter = ('restaurant', 'weekday')
    search_fields = ('restaurant__name', 'weekday')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'max_seats', 'is_open_now')
    list_filter = ('owner',)
    search_fields = ('name', 'description')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'id')
    list_filter = ('restaurant',)
    search_fields = ('restaurant__name',)

@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ('menu', 'sname')
    list_filter = ('menu__restaurant',)
    search_fields = ('sname',)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('section', 'dname', 'description', 'price')
    list_filter = ('section__menu__restaurant',)
    search_fields = ('dname', 'description')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'date', 'time', 'number_of_people')
    list_filter = ('restaurant', 'user', 'date')
    search_fields = ('restaurant__name', 'user__username')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'date', 'status', 'total_price', 'is_retired')
    list_filter = ('restaurant', 'user', 'status')
    search_fields = ('restaurant__name', 'user__username')

@admin.register(ActiveOrderItem)
class ActiveOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'dish', 'quantity')
    list_filter = ('order__restaurant',)
    search_fields = ('dish__dname', 'order__restaurant__name')