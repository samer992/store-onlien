from rest_framework import serializers

from shop.serializers import ProductsSerializer
from .models import *

class ModulerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModuler
        fields = "__all__"


class MoudulerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModulerModel
        fields = "__all__"

class MoudulerUserSerializer(serializers.ModelSerializer):
    productsmoduler = serializers.SerializerMethodField(method_name="get_products_moduler", read_only=True)
    moduler_profile = serializers.SerializerMethodField(method_name="get_moduler_profile", read_only=True)
    # closeDay = serializers.SerializerMethodField(method_name="get_moduler_closed", read_only=True)

    class Meta:
        model = ModulerUserModel
        fields = "__all__"


    def get_moduler_profile(self, obj):

        moduler_profile = obj.modulerprof

        serializer = ModulerProfileSerializer(instance=moduler_profile, many=True)
        return serializer.data


    def get_products_moduler(self, obj):
        # print(obj)
        # if obj.name == "محل":
            user_emp = obj.productsmoduler

            serializer = ProductsSerializer(user_emp, many=True)
            return serializer.data

    def get_moduler_closed(self, obj):

        moduler_closed = obj.modulerclosed

        serializer = ModulerProfileSerializer(instance=moduler_closed, many=True)
        return serializer.data
