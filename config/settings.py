# config/settings.py (agregar estas configuraciones)

# Configuración de Google Analytics
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GA_TRACKING_ID', '')
GOOGLE_ANALYTICS_API_CREDENTIALS = os.environ.get('GA_API_CREDENTIALS', '')

# Apps instaladas - agregar las nuevas apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps del ecommerce
    'accounts',
    'products',
    'cart',
    'checkout',
    'payments',
    'orders',      # Tu app de pedidos
    'dashboard',   # Tu app de dashboard
    'analytics',   # Tu app de analytics
    
    # Third party apps
    'rest_framework',
    'corsheaders',
]

# Configuración de REST Framework para APIs
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Configuración de CORS (si vas a usar frontend separado)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

# Configuración de logging para analytics
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'analytics.log',
        },
    },
    'loggers': {
        'analytics': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configuración de tareas programadas (con Celery)
# Si decides usar Celery para tareas automáticas
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Argentina/Cordoba'

# Configuración específica para el dashboard
DASHBOARD_CONFIG = {
    'ITEMS_PER_PAGE': 20,
    'MAX_CHART_DAYS': 365,
    'DEFAULT_CHART_DAYS': 30,
    'ENABLE_REAL_TIME_METRICS': True,
}