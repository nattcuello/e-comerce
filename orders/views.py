from rest_framework import viewsets
from .models import (
    Product, PaymentMethod, PaymentStatus, Persona, Company,
    FiscalCondition, CardInfo, Order, OrderDetail, OrderDetailCard
)
from .serializers import (
    ProductSerializer, PaymentMethodSerializer, PaymentStatusSerializer, PersonaSerializer,
    CompanySerializer, FiscalConditionSerializer, CardInfoSerializer,
    OrderSerializer, OrderDetailSerializer, OrderDetailCardSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer


class PaymentStatusViewSet(viewsets.ModelViewSet):
    queryset = PaymentStatus.objects.filter(is_active=True)
    serializer_class = PaymentStatusSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.filter(is_active=True)
    serializer_class = PersonaSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer


class FiscalConditionViewSet(viewsets.ModelViewSet):
    queryset = FiscalCondition.objects.filter(is_active=True)
    serializer_class = FiscalConditionSerializer




class CardInfoViewSet(viewsets.ModelViewSet):
    queryset = CardInfo.objects.filter(is_active=True)
    serializer_class = CardInfoSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = OrderSerializer


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.filter(is_active=True)
    serializer_class = OrderDetailSerializer


class OrderDetailCardViewSet(viewsets.ModelViewSet):
    queryset = OrderDetailCard.objects.filter(is_active=True)
    serializer_class = OrderDetailCardSerializer
