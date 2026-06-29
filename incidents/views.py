from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Restaurant, MenuItem, Order, OrderItem, Payment, DeliveryTracking
from decimal import Decimal
import requests
from django.conf import settings as django_settings


# ---------- AUTH ----------
def home(request):
    restaurants = Restaurant.objects.filter(is_active=True)[:6]
    popular_items = MenuItem.objects.filter(is_available=True)[:6]
    return render(request, 'incidents/home.html', {
        'restaurants': restaurants,
        'popular_items': popular_items,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FoodieExpress, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'incidents/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'incidents/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ---------- RESTAURANTS ----------
def restaurant_list(request):
    restaurants = Restaurant.objects.filter(is_active=True)
    return render(request, 'incidents/restaurants.html', {'restaurants': restaurants})


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.filter(is_available=True)
    return render(request, 'incidents/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })


# ---------- ORDERS ----------
@login_required
def place_order(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')
        delivery_address = request.POST.get('delivery_address')

        if not item_ids:
            messages.error(request, 'Please select at least one item.')
            return redirect('restaurant_detail', pk=restaurant_id)

        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            delivery_address=delivery_address,
        )

        total = Decimal('0.00')
        for item_id, qty in zip(item_ids, quantities):
            qty = int(qty)
            if qty > 0:
                item = get_object_or_404(MenuItem, pk=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=qty,
                    price=item.price,
                )
                total += item.price * qty

        order.total_price = total
        order.save()

        DeliveryTracking.objects.create(order=order)

        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('checkout', order_id=order.id)

    return redirect('restaurant_detail', pk=restaurant_id)


@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'incidents/checkout.html', {
        'order': order,
        'flutterwave_public_key': django_settings.FLUTTERWAVE_PUBLIC_KEY,
    })


@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        method = request.POST.get('payment_method')
        Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_price,
            method=method,
            status='completed',
        )
        order.status = 'confirmed'
        order.save()
        messages.success(request, 'Payment successful! Your order is confirmed.')
        return redirect('track_order', order_id=order.id)
    return redirect('checkout', order_id=order_id)


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    tracking = getattr(order, 'tracking', None)
    return render(request, 'incidents/track_order.html', {
        'order': order,
        'tracking': tracking,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'incidents/my_orders.html', {'orders': orders})

@login_required
def verify_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    transaction_id = request.GET.get('transaction_id')

    # Verify with Flutterwave
    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'
    }
    response = requests.get(
        f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify',
        headers=headers
    )
    data = response.json()

    if data['status'] == 'success' and \
       float(data['data']['amount']) >= float(order.total_price):
        # Payment confirmed
        Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_price,
            method='card',
            status='completed',
        )
        order.status = 'confirmed'
        order.save()
        messages.success(request, 'Payment successful! Order confirmed.')
        return redirect('track_order', order_id=order.id)
    else:
        messages.error(request, 'Payment verification failed.')
        return redirect('checkout', order_id=order.id)