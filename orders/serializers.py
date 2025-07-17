from rest_framework import serializers
from .models import (
    Product, PaymentMethod, PaymentStatus, Persona, Company,
    FiscalCondition, CardInfo, Order, OrderDetail, OrderDetailCard
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_active']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'is_active']


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = ['id', 'name', 'is_active']


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'name', 'is_active']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'is_active']


class FiscalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalCondition
        fields = ['id', 'name', 'is_active']




class CardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardInfo
        fields = ['id', 'payment_method', 'card_holder', 'card_number', 'expiration', 'is_active']


class OrderDetailSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'product', 'quantity', 'unit_price', 'subtotal', 'is_active']

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderDetailCardSerializer(serializers.ModelSerializer):
    unit_price_with_offer = serializers.SerializerMethodField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)
    total_installments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderDetailCard
        fields = [
            'id', 'order', 'product', 'card_info', 'cuotas', 'quantity',
            'unit_price', 'offer', 'discount', 'unit_price_with_offer',
            'subtotal', 'total_installments', 'is_active'
        ]

    def get_unit_price_with_offer(self, obj):
        return obj.unit_price_with_offer

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_total_installments(self, obj):
        return obj.total_installments


class OrderSerializer(serializers.ModelSerializer):
    standard_items = OrderDetailSerializer(many=True, read_only=True)
    card_items = OrderDetailCardSerializer(many=True, read_only=True)
    total_standard = serializers.SerializerMethodField(read_only=True)
    total_card = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'company', 'persona', 'status',
            'payment_status', 'estimated_delivery', 'fiscal_condition',
            'shipping_address', 'shipping_city',
            'shipping_postal_code', 'shipping_phone', 'notes',
            'shipping_cost', 'tax_amount', 'total',
            'total_standard', 'total_card', 'total_amount',
            'created_at', 'is_active', 'standard_items', 'card_items'
        ]

    def get_total_standard(self, obj):
        return obj.get_total_standard()

    def get_total_card(self, obj):
        return obj.get_total_card()

    def get_total_amount(self, obj):
        return obj.get_total()
