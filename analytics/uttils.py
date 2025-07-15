# Importaciones necesarias para conectar con Google Analytics y Django
from google.analytics.data_v1beta import BetaAnalyticsDataClient  # Cliente para consultas a Analytics
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric  # Estructuras de la consulta
from google.oauth2 import service_account  # Autenticación con credenciales de servicio
from django.conf import settings  # Configuración de Django (IDs y rutas de credenciales)

# Crea y devuelve un cliente autenticado de Google Analytics
def get_analytics_client():
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_ANALYTICS_CREDENTIALS
    )
    return BetaAnalyticsDataClient(credentials=credentials)

# Obtiene vistas de página por fecha (últimos 7 días)
def get_page_views():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    response = client.run_report(request)
    return [
        {
            "date": row.dimension_values[0].value,
            "views": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Devuelve los 10 productos más comprados en los últimos 30 días
def get_top_products():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="itemName")],
        metrics=[Metric(name="purchaseQuantity")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=10,
    )
    response = client.run_report(request)
    return [
        {
            "product": row.dimension_values[0].value,
            "quantity_sold": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Obtiene los 20 productos más agregados al carrito (últimos 30 días)
def get_most_added_to_cart():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="itemName")],
        metrics=[Metric(name="addToCartQuantity")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=20,
    )
    response = client.run_report(request)
    return [
        {
            "product": row.dimension_values[0].value,
            "added_to_cart": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Retorna usuarios activos por fecha (últimos 7 días)
def get_active_users():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    response = client.run_report(request)
    return [
        {
            "date": row.dimension_values[0].value,
            "active_users": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Cuenta registros diarios según evento de engagement (p. ej. "sign_up")
def get_user_registrations():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="userEngagementEvents")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    response = client.run_report(request)
    return [
        {
            "date": row.dimension_values[0].value,
            "registrations": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Mide usuarios activos por hora en el día actual
def get_hourly_traffic():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        dimensions=[Dimension(name="hour")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="today", end_date="today")],
    )
    response = client.run_report(request)
    return [
        {
            "hour": row.dimension_values[0].value,
            "active_users": int(row.metric_values[0].value)
        }
        for row in response.rows
    ]

# Obtiene los ingresos totales de compras en los últimos 30 días
def get_total_revenue():
    client = get_analytics_client()
    request = RunReportRequest(
        property=f"properties/{settings.GOOGLE_ANALYTICS_PROPERTY_ID}",
        metrics=[Metric(name="purchaseRevenue")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    response = client.run_report(request)

    for row in response.rows:
        return {"total_revenue": float(row.metric_values[0].value)}

    return {"total_revenue": 0}

