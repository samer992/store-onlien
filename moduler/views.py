from django.shortcuts import render, redirect
from requests import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.serializers import UserSerializer
from .models import *
from .serializer import MoudulerUserSerializer, MoudulerSerializer
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
# from .models import ModulerModel
from rest_framework.response import Response

# Create your views here.

# class Moduler(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = MoudulerSerializer
#     parsers_classes = [MultiPartParser, FormParser]
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxx")
#
#     # @swagger_auto_schema(operation_summary="Get all Orders")
#     def post(self, request, format=None):
#         name_burshios = ModulerModel.objects.filter(user=request.user, name=request.data["name"])
#         if name_burshios:
#             return Response({"data": "الاسم متاخد"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             add_Moduler = ModulerModel()
#             add_name_burshios.user = request.user
#             add_name_burshios.name = request.data["name"]
#             add_name_burshios.save()
#             return Response({"data": f"تم اضافه {request.data['name']} بنجاح "}, status=status.HTTP_201_CREATED)
#
#     def get(self, request):
#         name_burshios = ModulerModel.objects.filter(user=request.user)
#         serializer = self.serializer_class(instance=name_burshios, many=True)
#         # if serializer.is_valid(raise_exception=True):
#         # serializer.save()
#         # product = serializer.data
#         # print(product)
#
#         return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def modulers(request):
    user = request.user
    if user.emp:
        user_man = User.objects.get(id=user.manageid)
        # print("its emp")
    else:
        user_man = request.user
    # print(user)
    userman = UserManage.objects.get(user=user_man)
    # print(userman)
    moduler = ModulerUserModel.objects.filter(usermanage=userman)
    # print(moduler[0]["moduler_profile"][0]["shop_name"])

    serializer = MoudulerUserSerializer(instance=moduler, many=True)
    print(serializer.data[0]["moduler_profile"][0]["shop_name"])
    return Response({"modulers": serializer.data}, status=status.HTTP_200_OK)

def addmoduler(request, modu):
    # print(request.user)
    usermanage = UserManage.objects.get(user=request.user)
    moduler = ModulerModel.objects.get(id=modu)
    print(moduler)
    print(usermanage)
    add_moduler = ModulerUserModel()
    add_moduler.name = moduler.name
    add_moduler.namee = moduler.namee

    add_moduler.namepath = moduler.namepath
    add_moduler.imgmoduler = moduler.imgmoduler
    add_moduler.usermanage = usermanage
    add_moduler.save()
    return redirect("informathion")

@api_view(['GET'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def localdata(request):
    user = request.user
    serializer = UserSerializer(instance=user, many=False)
    # print(serializer.data)
    return Response({"mymodulers": serializer.data["userman"]["mymodulers"]}, status=status.HTTP_200_OK)
