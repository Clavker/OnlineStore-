from django.urls import path
from . import views

urlpatterns = [
    # Products
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/update/', views.product_update,
         name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete,
         name='product_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/', views.category_detail,
         name='category_detail'),
    path('categories/<int:pk>/update/', views.category_update,
         name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete,
         name='category_delete'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update,
         name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete,
         name='customer_delete'),

    # Carts
    path('carts/', views.cart_list, name='cart_list'),
    path('carts/<int:pk>/', views.cart_detail, name='cart_detail'),
    path('carts/create/', views.cart_create, name='cart_create'),
    path('carts/<int:pk>/add-item/', views.cart_add_item,
         name='cart_add_item'),
    path('carts/item/<int:pk>/update/', views.cart_item_update,
         name='cart_item_update'),
    path('carts/item/<int:pk>/delete/', views.cart_item_delete,
         name='cart_item_delete'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/create-from-cart/<int:cart_id>/',
         views.order_create_from_cart, name='order_create_from_cart'),
    path('orders/<int:pk>/update-status/', views.order_update_status,
         name='order_update_status'),
]