from django.shortcuts import render, redirect, get_object_or_404
from ..forms.dashboard_forms import RestaurantForm, AddressForm, DishForm, MenuSectionForm, OpeningHoursForm
from ..models import Menu, Restaurant, OpeningHours, MenuSection, Dish, Reservation
from django.contrib.auth.decorators import login_required
from ..utils.decorators import user_has_restaurant
from ..utils.constants import WEEKDAYS
from ..utils.functions import get_incomplete_fields

@login_required
def create_restaurant(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, user=request.user)
        if address_form.is_valid() and restaurant_form.is_valid():
            # Save the Address
            address = address_form.save()

            # Save the Restaurant
            restaurant = restaurant_form.save(commit=False)
            restaurant.address = address
            restaurant.owner = request.user  # Assuming user is logged in
            restaurant.save()

            menu = Menu(restaurant=restaurant)
            menu.save()

            return redirect('restaurants:dashboard')  # Redirect to restaurant detail view
    else:
        address_form = AddressForm()
        restaurant_form = RestaurantForm(user=request.user)

    return render(request, 'restaurants/restaurant-create.html', {'address_form': address_form, 'restaurant_form': restaurant_form, 'title':'Register your restaurant'})



@login_required
@user_has_restaurant
def dashboard(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    incomplete_fields = get_incomplete_fields(restaurant)

    context = {
        'restaurant': restaurant,
        'incomplete_fields': incomplete_fields,
    }
    return render(request, 'restaurants/dashboard.html', context)

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
    return render(request, 'restaurants/menu-section.html', {'form': form, 'restaurant': restaurant})

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
    return render(request, 'restaurants/menu-section.html', {'form': form, 'section': section, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def delete_section(request, section_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    section = get_object_or_404(MenuSection, pk=section_id)
    if request.method == 'POST':
        section.delete()
        return redirect('restaurants:add_section') 
    return render(request, 'restaurants/menu-section.html', {'section': section, 'restaurant': restaurant})


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
    return render(request, 'restaurants/menu-dishes.html', {'form': form, 'restaurant': restaurant})

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
    return render(request, 'restaurants/menu-dishes.html', {'form': form, 'restaurant': restaurant,'dish': dish})

def delete_dish(request, dish_id):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    dish = get_object_or_404(Dish, pk=dish_id)
    if request.method == 'POST':
        dish.delete()
        return redirect('restaurants:add_dish')
    return render(request, 'restaurants/menu-dishes.html', {'dish': dish, 'restaurant': restaurant})

@login_required
@user_has_restaurant
def set_address(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()

    # Get the existing address for the user's restaurant, if it exists
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

    return render(request, 'restaurants/address.html', {'form': form, 'restaurant': restaurant})

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

    return render(request, 'restaurants/openinghours.html', {'form': form, 'opening_hours': organized_opening_hours})

@login_required
@user_has_restaurant
def delete_opening_hour(request, pk):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    opening_hour = get_object_or_404(OpeningHours, pk=pk, restaurant=restaurant)

    if request.method == 'POST':
        opening_hour.delete()
        return redirect('restaurants:set_opening_hours')  # or any other view you want to redirect to

    return render(request, 'restaurants/openinghours.html', {'restaurant': restaurant})

@user_has_restaurant
@login_required
def view_all_reservations(request):
    reservations = Reservation.objects.filter(restaurant__owner=request.user).order_by('date', 'time')
    return render(request, 'restaurants/restaurant-reservation.html', {'reservations': reservations})
