from django.contrib import admin
from .models import Restaurant, MenuItem, Order, OrderItem, Payment, DeliveryTracking

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'delivery_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'category', 'is_available']
    list_filter = ['category', 'is_available', 'restaurant']
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'restaurant', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['user__username']
    actions = ['mark_confirmed', 'mark_preparing', 'mark_on_the_way', 'mark_delivered']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = 'Mark as Confirmed'

    def mark_preparing(self, request, queryset):
        queryset.update(status='preparing')
    mark_preparing.short_description = 'Mark as Preparing'

    def mark_on_the_way(self, request, queryset):
        queryset.update(status='on_the_way')
    mark_on_the_way.short_description = 'Mark as On The Way'

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_delivered.short_description = 'Mark as Delivered'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'amount', 'method', 'status']
    list_editable = ['status']
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = 'Mark as Completed'

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'driver_name', 'driver_phone', 'current_location']