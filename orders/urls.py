# orders/urls.py (APIs para pedidos)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)

app_name = 'orders'

urlpatterns = [
    # APIs REST para pedidos
    path('api/', include(router.urls)),
    
    # Endpoints específicos
    path('api/orders/<int:order_id>/tracking/', views.order_tracking, name='order_tracking'),
    path('api/orders/user/<int:user_id>/', views.user_orders, name='user_orders'),
]


# requirements.txt (dependencias del proyecto)
"""
Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
celery>=5.2.0
redis>=4.5.0
psycopg2-binary>=2.9.0  # Para PostgreSQL
Pillow>=9.5.0  # Para manejo de imágenes
python-decouple>=3.8  # Para variables de entorno
requests>=2.31.0  # Para APIs externas (Google Analytics, MercadoPago)
"""

# .env.example (archivo de ejemplo para variables de entorno)
"""
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/ecommerce_db

# Django
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis (para Celery)
REDIS_URL=redis://localhost:6379

# Google Analytics
GA_TRACKING_ID=UA-XXXXXXXXX-X
GA_API_CREDENTIALS=path/to/credentials.json

# MercadoPago (para la integración de pagos)
MERCADOPAGO_ACCESS_TOKEN=tu-access-token
MERCADOPAGO_PUBLIC_KEY=tu-public-key

# Email (para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
"""