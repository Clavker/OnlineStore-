from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('products/', include('main.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)