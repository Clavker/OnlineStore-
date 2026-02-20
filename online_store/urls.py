from django.contrib import admin
from django.urls import path, include
from main import views  # импортируем views

urlpatterns = [
    path('', views.home_view, name='home'),  # главная страница
    path('admin/', admin.site.urls),
    path('products/', include('main.urls')),  # все остальные страницы с префиксом /products/
    path('accounts/', include('django.contrib.auth.urls')),
]