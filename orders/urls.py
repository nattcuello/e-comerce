from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, PaymentMethodViewSet, PaymentStatusViewSet, PersonaViewSet,
    CompanyViewSet, FiscalConditionViewSet, CardInfoViewSet,
    OrderViewSet, OrderDetailViewSet, OrderDetailCardViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'payment-statuses', PaymentStatusViewSet)
router.register(r'personas', PersonaViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'fiscal-conditions', FiscalConditionViewSet)
router.register(r'card-info', CardInfoViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-details', OrderDetailViewSet)
router.register(r'order-detail-cards', OrderDetailCardViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
