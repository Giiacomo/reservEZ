from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Restaurant, MenuSection, Reservation, Order, ActiveOrderItem, Dish
from accounts.models import UserProfile
from ..forms.restaurants_forms import ReservationForm, OrderItemForm
from ..utils.decorators import check_restaurant_complete, filter_complete_restaurants
from ..utils.functions import is_restaurant_open

@login_required
def add_to_order(request, restaurant_id, dish_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # Get the quantity from the form
        dish = get_object_or_404(Dish, pk=dish_id)
        order, _ = Order.objects.get_or_create(restaurant_id=restaurant_id, user=request.user, status='NS')

        # Check if the dish is already in the order, update the quantity
        active_item = ActiveOrderItem.objects.filter(order=order, dish=dish).first()
        if active_item:
            active_item.quantity += quantity
            active_item.save()
        else:
            # Create a new order item
            order_item = ActiveOrderItem.objects.create(order=order, dish=dish, quantity=quantity)

        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)
    else:
        # Handle GET request or invalid form data
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)

@login_required
def delete_from_order(request, restaurant_id, item_id):
    item = get_object_or_404(ActiveOrderItem, pk=item_id)

    if item.order.restaurant_id == restaurant_id and item.order.user == request.user:
        item.delete()

    return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)

@login_required
def submit_order(request, restaurant_id):
    try:
        order = Order.objects.get(restaurant_id=restaurant_id, user=request.user, status='NS')
        order.status = 'AW'  # Set status to 'AW' (Awaiting Acceptance)
        order.save()
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)
    except Order.DoesNotExist:
        # Handle the case where there is no active order or the order is already submitted
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant-list.html', {'restaurants': restaurants, 'title': 'List of restaurants:'})

@check_restaurant_complete
@login_required
def restaurant_page(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_sections = MenuSection.objects.filter(menu__restaurant=restaurant)
    user_reservations = Reservation.objects.filter(restaurant=restaurant, user=request.user)
    
    order = Order.objects.filter(restaurant=restaurant, user=request.user).exclude(status='T').first()

    context = {
        'restaurant': restaurant,
        'menu_sections': menu_sections,
        'user_reservations': user_reservations,
        'order': order,  # Pass the order to the template
    }
    return render(request, 'restaurants/restaurant-page.html', context)

@filter_complete_restaurants
def user_homepage(request):
    # Fetch user profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Get user's city from the address associated with the user profile
    user_city = user_profile.address.city if user_profile.address else None

    # Use the filtered complete restaurants
    complete_restaurants = request.complete_restaurants

    # Create lists to store restaurant data based on different categories
    in_city_open = []
    in_city_closed = []
    outside_city_open = []
    outside_city_closed = []

    for restaurant in complete_restaurants:
        restaurant_data = {
            'restaurant': restaurant,
            'inCity': restaurant.address.city == user_city,
            'isOpen': is_restaurant_open(restaurant)
        }
        if restaurant_data['inCity']:
            if restaurant_data['isOpen']:
                in_city_open.append(restaurant_data)
            else:
                in_city_closed.append(restaurant_data)
        else:
            if restaurant_data['isOpen']:
                outside_city_open.append(restaurant_data)
            else:
                outside_city_closed.append(restaurant_data)

    # Concatenate lists to create the final ordered list
    restaurant_data_list = in_city_open + in_city_closed + outside_city_open + outside_city_closed

    context = {
        'restaurant_data_list': restaurant_data_list,
    }
    return render(request, 'restaurants/homepage.html', context)

@login_required
def make_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    opening_hours = restaurant.opening_hours.all()
    if request.method == 'POST':
        form = ReservationForm(request.POST, user=request.user, restaurant=restaurant)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant = restaurant
            reservation.save()
            return redirect('restaurants:restaurant_page', restaurant_id=restaurant.id)
    else:
        form = ReservationForm(user=request.user, restaurant=restaurant)

    return render(request, 'restaurants/reservation.html', {
        'form': form,
        'restaurant': restaurant,
        'opening_hours': opening_hours,

    })

@login_required
def delete_reservation(request, restaurant_id, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user, restaurant_id=restaurant_id)
    reservation.delete()
    return redirect('restaurants:restaurant_page', restaurant_id=reservation.restaurant.id)
