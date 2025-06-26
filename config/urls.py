# config/urls.py (URLs principales del proyecto)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/auth/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/checkout/', include('checkout.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/orders/', include('orders.urls')),
    
    # Dashboard administrativo
    path('dashboard/', include('dashboard.urls')),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar el admin de Django
admin.site.site_header = "Ecommerce Admin"
admin.site.site_title = "Ecommerce Admin Portal"
admin.site.index_title = "Bienvenido al Panel de Administración"

