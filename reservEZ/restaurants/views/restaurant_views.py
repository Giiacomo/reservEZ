from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Restaurant, Tag, MenuSection, Reservation, Order, ActiveOrderItem, Dish
from accounts.models import UserProfile
from ..forms.restaurants_forms import ReservationForm, OrderItemForm
from ..utils.decorators import check_restaurant_complete, filter_complete_restaurants
from ..utils.functions import generate_recommendations, filter_restaurants
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import timedelta, datetime

@require_GET
def get_time_choices(request):
    date_str = request.GET.get('date')
    restaurant_id = request.GET.get('restaurant_id')

    if not date_str or not restaurant_id:
        return JsonResponse({'time_choices': []})

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'time_choices': []})

    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    weekday = date.weekday()
    opening_hours = restaurant.opening_hours.filter(weekday=weekday).first()

    if not opening_hours:
        return JsonResponse({'time_choices': []})

    opening_time = datetime.combine(date, opening_hours.opening_time)
    closing_time = datetime.combine(date, opening_hours.closing_time)
    times = []
    while opening_time <= closing_time:
        times.append((opening_time.strftime('%H:%M'), opening_time.strftime('%H:%M')))
        opening_time += timedelta(minutes=15)

    return JsonResponse({'time_choices': times})

@login_required
def add_to_order(request, restaurant_id, dish_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  
        dish = get_object_or_404(Dish, pk=dish_id)
        order, _ = Order.objects.get_or_create(restaurant_id=restaurant_id, user=request.user, status='NS')

        
        active_item = ActiveOrderItem.objects.filter(order=order, dish=dish).first()
        if active_item:
            active_item.quantity += quantity
            active_item.save()
        else:
            
            order_item = ActiveOrderItem.objects.create(order=order, dish=dish, quantity=quantity)

        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)
    else:
        
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)

@login_required
def delete_order(request, restaurant_id, order_id):
    order = get_object_or_404(Order, pk=order_id, restaurant_id=restaurant_id, user=request.user)
    
    if order.status == 'NS':  
        order.delete()
        
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
        order.status = 'AW'  
        order.save()
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)
    except Order.DoesNotExist:
        
        return redirect('restaurants:restaurant_page', restaurant_id=restaurant_id)

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/public/restaurant-list.html', {'restaurants': restaurants, 'title': 'List of restaurants:'})

@check_restaurant_complete
def restaurant_page(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_sections = MenuSection.objects.filter(menu__restaurant=restaurant)

    user_reservations = None
    order = None
    if request.user.is_authenticated:
        user_reservations = Reservation.objects.filter(restaurant=restaurant, user=request.user)
        order = Order.objects.filter(restaurant=restaurant, user=request.user).exclude(status='T').first()

    context = {
        'restaurant': restaurant,
        'menu_sections': menu_sections,
        'user_reservations': user_reservations,
        'order': order,  
    }
    return render(request, 'restaurants/public/restaurant-page.html', context)
    

@filter_complete_restaurants
def user_homepage(request):
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)

    cities = Restaurant.objects.values_list('address__city', flat=True).distinct()
    tag_choices = Tag.objects.all()

    
    search_query = request.GET.get('q', '')
    selected_city = request.GET.get('city', '')
    selected_tag = request.GET.get('tag', '')

    user_city = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        user_city = user_profile.address.city if user_profile.address else None

    filtered_restaurants = filter_restaurants(search_query, selected_city, selected_tag, user_city, restaurants=request.complete_restaurants)
    
    for restaurant in filtered_restaurants:
        restaurant.is_open = restaurant.is_open_now()
    recommended_restaurants = None
    if request.user.is_authenticated:
        recommended_restaurants = generate_recommendations(request.user, filtered_restaurants)

    context = {
        'recommended_restaurants': recommended_restaurants,
        'all_restaurants': filtered_restaurants,
        'cities': cities,
        'tag_choices': tag_choices,
        'selected_city': selected_city,
        'selected_tag': selected_tag,
        'search_query': search_query,
        'user_profile': user_profile,
    }
    
    return render(request, 'restaurants/public/homepage.html', context)

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
            reservation.date = form.cleaned_data['date']  
            reservation.save()
            return redirect('restaurants:restaurant_page', restaurant_id=restaurant.id)
    else:
        form = ReservationForm(user=request.user, restaurant=restaurant)

    return render(request, 'restaurants/public/reservation.html', {
        'form': form,
        'restaurant': restaurant,
        'opening_hours': opening_hours,
    })

@login_required
def delete_reservation(request, restaurant_id, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user, restaurant_id=restaurant_id)
    reservation.delete()
    return redirect('restaurants:restaurant_page', restaurant_id=reservation.restaurant.id)
