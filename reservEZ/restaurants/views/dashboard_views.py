from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..forms.dashboard_forms import RestaurantForm, RestaurantTagForm, AddressForm, DishForm, MenuSectionForm, OpeningHoursForm, LogoUploadForm, BannerUploadForm, SeatsForm
from ..models import Menu, Restaurant, OpeningHours, MenuSection, Dish, Reservation, Order, ActiveOrderItem
from ..utils.decorators import user_has_restaurant
from ..utils.constants import WEEKDAYS, STATUS_CHOICES
from ..utils.functions import get_incomplete_fields
from django.db import transaction

@login_required
@user_has_restaurant
def upload_logo(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if request.method == 'POST':
        form = LogoUploadForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurants:dashboard')
    else:
        form = LogoUploadForm(instance=restaurant)
    return render(request, 'restaurants/dashboard/upload-logo.html', {'form': form})

@login_required
@user_has_restaurant
def upload_banner(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if request.method == 'POST':
        form = BannerUploadForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurants:dashboard')
    else:
        form = BannerUploadForm(instance=restaurant)
    return render(request, 'restaurants/dashboard/upload-banner.html', {'form': form})

@login_required
@user_has_restaurant
def manage_orders(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    orders = Order.objects.filter(restaurant=restaurant).order_by('date').reverse() 
    active_orders = [order for order in orders if not order.is_retired()]

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        if not order.is_retired():
            order.status = new_status
            order.save()
        return redirect('restaurants:manage_orders')

    context = {
        'restaurant': restaurant,
        'orders': active_orders,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, 'restaurants/dashboard/manage-orders.html', context)


@login_required
def create_restaurant(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, user=request.user)
        
        if address_form.is_valid() and restaurant_form.is_valid():
            with transaction.atomic():
            
                address = address_form.save()

            
                restaurant = restaurant_form.save(commit=False)
                restaurant.address = address
                restaurant.owner = request.user
                restaurant.save() 

            
                menu = Menu.objects.create(restaurant=restaurant)

            return redirect('restaurants:dashboard')
    else:
        address_form = AddressForm()
        restaurant_form = RestaurantForm(user=request.user)

    return render(request, 'restaurants/dashboard/restaurant-create.html', {
        'address_form': address_form,
        'restaurant_form': restaurant_form,
        'title': 'Register your restaurant'
    })

    
@login_required
@user_has_restaurant
def dashboard(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    incomplete_fields = get_incomplete_fields(restaurant)

    context = {
        'restaurant': restaurant,
        'incomplete_fields': incomplete_fields,
    }
    return render(request, 'restaurants/dashboard/dashboard.html', context)

@login_required
@user_has_restaurant
def add_section(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    menu = restaurant.menu.first()
    if request.method == 'POST':
        form = MenuSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.menu = menu
            section.save()
            form = MenuSectionForm()
    else:
        form = MenuSectionForm()
    return render(request, 'restaurants/dashboard/menu-section.html', {'form': form, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def modify_section(request, section_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    section = get_object_or_404(MenuSection, pk=section_id)
    if request.method == 'POST':
        form = MenuSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('restaurants:add_section') 
    else:
        form = MenuSectionForm(instance=section)
    return render(request, 'restaurants/dashboard/menu-section.html', {'form': form, 'section': section, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def delete_section(request, section_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    section = get_object_or_404(MenuSection, pk=section_id)
    if request.method == 'POST':
        section.delete()
        return redirect('restaurants:add_section') 
    return render(request, 'restaurants/dashboard/menu-section.html', {'section': section, 'restaurant': restaurant})


@login_required
@user_has_restaurant
def add_dish(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    menu = restaurant.menu.first()
    if request.method == 'POST':
            form = DishForm(request.POST, restaurant=restaurant)
            if form.is_valid():
                dish = form.save(commit=False)
                dish.menu = menu
                dish.save()
                form = DishForm(restaurant=restaurant)
    else:
        form = DishForm(restaurant=restaurant)
    return render(request, 'restaurants/dashboard/menu-dishes.html', {'form': form, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def modify_dish(request, dish_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    dish = get_object_or_404(Dish, pk=dish_id)
    if request.method == 'POST':
        form = DishForm(request.POST, instance=dish)
        if form.is_valid():
            form.save()
            return redirect('restaurants:add_dish')
    else:
        form = DishForm(instance=dish)
    return render(request, 'restaurants/dashboard/menu-dishes.html', {'form': form, 'restaurant': restaurant,'dish': dish})

def delete_dish(request, dish_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    dish = get_object_or_404(Dish, pk=dish_id)
    if request.method == 'POST':
        dish.delete()
        return redirect('restaurants:add_dish')
    return render(request, 'restaurants/dashboard/menu-dishes.html', {'dish': dish, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def set_address(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()


    existing_address = restaurant.address if restaurant else None

    if request.method == 'POST':
        form = AddressForm(request.POST, existing_address=existing_address)
        if form.is_valid():
            new_address = form.save()
            restaurant.address = new_address
            restaurant.save() 
            if existing_address:
                existing_address.delete()   
    else:
        form = AddressForm(existing_address=existing_address)

    return render(request, 'restaurants/dashboard/address.html', {'form': form, 'restaurant': restaurant})

def set_opening_hours(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    opening_hours = restaurant.opening_hours.all()

    if request.method == 'POST':
        form = OpeningHoursForm(request.POST)
        if form.is_valid():
            weekday = form.cleaned_data['weekday']
            opening_time = form.cleaned_data['opening_time']
            closing_time = form.cleaned_data['closing_time']
            existing_opening_hour = OpeningHours.objects.filter(restaurant=restaurant, weekday=weekday).first()
            if existing_opening_hour:
                existing_opening_hour.opening_time = opening_time
                existing_opening_hour.closing_time = closing_time
                existing_opening_hour.save()
            else:
                opening_hours_instance = form.save(commit=False)
                opening_hours_instance.restaurant = restaurant
                opening_hours_instance.save()
            return redirect('restaurants:set_opening_hours')
    else:
        form = OpeningHoursForm()

    organized_opening_hours = {}
    for weekday, _ in WEEKDAYS:
        opening_hour = opening_hours.filter(weekday=weekday).first()
        organized_opening_hours[weekday] = opening_hour

    return render(request, 'restaurants/dashboard/openinghours.html', {'form': form, 'opening_hours': organized_opening_hours})

@login_required
@user_has_restaurant
def delete_opening_hour(request, pk):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    opening_hour = get_object_or_404(OpeningHours, pk=pk, restaurant=restaurant)

    if request.method == 'POST':
        opening_hour.delete()
        return redirect('restaurants:set_opening_hours') 

    return render(request, 'restaurants/dashboard/openinghours.html', {'restaurant': restaurant})

@user_has_restaurant
@login_required
def view_all_reservations(request):
    reservations = Reservation.objects.filter(restaurant__owner=request.user).order_by('date', 'time')
    return render(request, 'restaurants/dashboard/restaurant-reservation.html', {'reservations': reservations})

@login_required
@user_has_restaurant
def order_detail(request, order_id):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    order_items = order.active_items.all()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

        return redirect('restaurants:order_detail', order_id=order_id)

    context = {
        'order': order,
        'order_items': order_items,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, 'restaurants/dashboard/order-detail.html', context)

@login_required
@user_has_restaurant
def retired_orders(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    orders = Order.objects.filter(restaurant=restaurant).order_by('date').reverse()
    retired_orders = [order for order in orders if order.is_retired()]
    context = {
        'restaurant': restaurant,
        'orders': retired_orders,
    }
    return render(request, 'restaurants/dashboard/retired-orders.html', context)

@login_required
@user_has_restaurant
def manage_tags(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    
    if request.method == 'POST':
        form = RestaurantTagForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurants:manage_tags') 
    else:
        form = RestaurantTagForm(instance=restaurant)
    
    return render(request, 'restaurants/dashboard/tags.html', {'form': form, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if request.user == reservation.restaurant.owner:
        if request.method == 'POST':
            reservation.delete()
            return redirect('restaurants:dashboard') 
        else:
            return render(request, 'restaurants/dashboard/delete_reservation.html', {'reservation': reservation})

@login_required
@user_has_restaurant
def set_seats(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if request.method == 'POST':
        form = SeatsForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurants:dashboard')
    else:
        form = SeatsForm(instance=restaurant)
    return render(request, 'restaurants/dashboard/seats.html', {'form': form})
