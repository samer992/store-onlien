import requests
from rest_framework import serializers
from .models import *
from rest_framework import status


class ProductsSerializer(serializers.ModelSerializer):
    productItems = serializers.SerializerMethodField(method_name="get_product_items", read_only=True)
    class Meta:
        model = Products
        fields = "__all__"

    def get_product_items(self, obj):
        product_items = obj.productitems.all()

        serializer = PriceBuyProductSerializer(product_items, many=True)
        return serializer.data


class PriceBuyProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceBuyProduct
        fields = "__all__"

class CatgoryProductTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CatgoryProductType
        fields = "__all__"



class OrderDetailsSerializer(serializers.ModelSerializer):
    get_full_total_sale = serializers.ReadOnlyField()
    get_puer_total_sale = serializers.ReadOnlyField()
    get_full_total_buy = serializers.ReadOnlyField()
    # password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    # password2 = serializers.CharField(max_length=100, min_length=6, write_only=True)

    class Meta:
        model = OrderDetails
        fields = "__all__"

class OrderBackDetailsSerializer(serializers.ModelSerializer):
    get_full_total_sale = serializers.ReadOnlyField()
    get_full_total_buy = serializers.ReadOnlyField()
    # password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    # password2 = serializers.CharField(max_length=100, min_length=6, write_only=True)

    class Meta:
        model = OrderDetails
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    orderItems = serializers.SerializerMethodField(method_name="get_order_items", read_only=True)
    # ordermanager = serializers.SerializerMethodField(method_name="get_order_name", read_only=True)


    class Meta:
        model = Order
        fields = "__all__"

    def get_order_items(self, obj):
        order_items = obj.orderitems.filter(is_finished=False)

        serializer = OrderDetailsSerializer(order_items, many=True)

        return serializer.data



class ClosedDaySerializer(serializers.ModelSerializer):
    closeempitems = serializers.SerializerMethodField(method_name="get_closeday_items", read_only=True)
    # buyManageItems = serializers.SerializerMethodField(method_name="get_buyManageItems", read_only=True)

    class Meta:
        model = ClosedDay
        fields = "__all__"

    def get_closeday_items(self, obj):
        closeemp_items = obj.closeempitems.all()

        serializer = ClosedEmpSerializer(instance= closeemp_items, many=True)
        #
        return serializer.data

    # def get_buyManageItems(self, obj):
    #     buy_Manage_Items = obj.buyManageItems.all()
    #
    #     serializer = BuyManagerSerializer(buy_Manage_Items, many=True)
    #
    #     return serializer.data

class ClosedEmpSerializer(serializers.ModelSerializer):
    closeordersitems = serializers.SerializerMethodField(method_name="get_close_orders_items", read_only=True)

    class Meta:
        model = ClosedEmp
        fields = "__all__"

    def get_close_orders_items(self, obj):
        close_orders_items = obj.closeordersitems.all()

        serializer = OrderSerializer(close_orders_items, many=True)
        #
        return serializer.data
