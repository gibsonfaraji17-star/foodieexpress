from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('accounts/login/', views.user_login, name='accounts_login'),

    # Restaurants
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),

    # Orders
    path('order/<int:restaurant_id>/', views.place_order, name='place_order'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('payment/verify/<int:order_id>/', views.verify_payment, name='verify_payment'),
]