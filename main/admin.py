from django.contrib import admin
from .models import (
    Category, Product, Customer,
    Cart, CartItem, Order, OrderItem,
    StockMovement
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий товаров"""
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    list_display = ('id', 'name', 'price', 'stock', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')
    fields = ('name', 'description', 'price', 'stock', 'category')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Админка для клиентов"""
    list_display = ('id', 'user', 'phone', 'city')
    search_fields = ('user__email', 'user__username', 'phone')
    list_filter = ('city', 'country')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админка для корзин"""
    list_display = ('id', 'customer', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Админка для позиций в корзине"""
    list_display = ('id', 'cart', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    list_display = (
        'id',
        'customer',
        'created_at',
        'status',
        'total_price'
    )
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для позиций заказа"""
    list_display = ('id', 'order', 'product', 'quantity', 'price')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Админка для движений товаров"""
    list_display = (
        'id',
        'product',
        'quantity',
        'movement_type',
        'created_at',
        'created_by'
    )
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'reference', 'comment')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('product', 'created_by')

    fieldsets = (
        ('Основное', {
            'fields': ('product', 'quantity', 'movement_type')
        }),
        ('Дополнительно', {
            'fields': ('reference', 'created_by', 'comment'),
            'classes': ('wide',)
        }),
        ('Системное', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )