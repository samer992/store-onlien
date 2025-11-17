import random

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserManage
from .serializers import *


# Create your views here.

class Tager(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagerSerializer

    def post(self, request, format=None):
        user = request.user
        if user.is_authenticated:
            manger_user = User.objects.get(id=user.manageid)
            tager_data = request.data
            manage = UserManage.objects.get(user=manger_user)
            moduler = ModulerUserModel.objects.get(usermanage=manage, id=tager_data["moduler"])

            tager = TagerModel()
            tager.usermanage = manger_user
            tager.user = user
            tager.name = tager_data["name"]
            tager.description = tager_data["description"]
            tager.address = tager_data["address"]
            tager.shop_name = tager_data["shop_name"]
            tager.moduler = moduler

            tager.save()
            for num in tager_data["phones"]:
                numphone = NumPhone()
                numphone.tager = tager
                numphone.phone = num
                numphone.save()


            return Response("تم بنجاح", status=status.HTTP_201_CREATED)
        return Response("سجل دخول", status=status.HTTP_423_LOCKED)


    def get(self, request):
        user = request.user
        if user.is_authenticated:
            manger_user = User.objects.get(id=user.manageid)

        togars = TagerModel.objects.filter(usermanage=manger_user)

        serializer = self.serializer_class(instance=togars, many=True)
        print(serializer.data)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)



class TagerInvoic(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagerInvoicModelSerializer

    def post(self, request):
        user = request.user
        if user.is_authenticated:
            barcode = random.randint(111111111111, 999999999999)
            invoice_data = request.data
            print(invoice_data)
            manger_user = User.objects.get(id=user.manageid)
            tager = TagerModel.objects.get(usermanage=manger_user, id=invoice_data["tager"])
            manage = UserManage.objects.get(user=manger_user)
            # manage = UserManage.objects.get(user=manger_user)
            moduler = ModulerUserModel.objects.get(usermanage=manage, id=int(invoice_data["moduler"]))
            invoice_items_data = invoice_data["invoiceitems"]
            invoice_total = 0
            for invoice_item in invoice_items_data:
                invoice_total += float(invoice_item["price_buy"]) * float(invoice_item["quantity"])

            # INVOICE ################################
            invoice = TagerInvoicModel()
            invoice.usermanage = manger_user
            invoice.user = user
            invoice.tager = tager
            invoice.moduler = moduler
            invoice.barcode_id = barcode
            invoice.total = invoice_total
            invoice.Payment = invoice_data["Payment"]
            invoice.stay = float(invoice_data["Payment"]) - invoice_total
            invoice.save()

            # INVOICEI ITEMS #########################
            for invoice_item_save in invoice_items_data:
                invoiceitems = TagerInvoicDetails()
                invoiceitems.invoice = invoice
                invoiceitems.name = invoice_item_save["name"]
                invoiceitems.description = invoice_item_save["description"]
                invoiceitems.quantity = invoice_item_save["quantity"]
                invoiceitems.price_buy = invoice_item_save["price_buy"]
                invoiceitems.type_quantity = invoice_item_save["type_quantity"]
                invoiceitems.save()

            # INVOICE DOF3AT #########################
            dof3a = TagerDof3atModel()
            dof3a.usermanage = manger_user
            dof3a.user = user
            dof3a.tager = tager
            dof3a.dof3a = invoice_data["Payment"]
            dof3a.description = "دفعه فى فاتوره"
            dof3a.save()

            return Response("تم بنجاح", status=status.HTTP_201_CREATED)
    def put(self, request):
        user = request.user
        if user.is_authenticated:
            manger_user = User.objects.get(id=user.manageid)



        return Response("تم بنجاح", status=status.HTTP_201_CREATED)
    # def get(self, request):
    #     user = request.user
    #     if user.is_authenticated:
    #         manger_user = request.user.manageid
    #         user_man = User.objects.get(id=manger_user)
    #
    #     tager_invoice = TagerInvoicModel.objects.filter(usermanage=user_man)
    #
    #     serializer = self.serializer_class(instance=tager_invoice, many=True)
    #     print(serializer.data)
    #     return Response({"data": serializer.data}, status=status.HTTP_200_OK)


