import datetime

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView

from employee.models import UserEmployee
from .serializers import SignupSerializer, LoginSerializer, SetNewPasswordSerializer, PasswordResetRequestSerializer, \
    LogoutUserSerializer, UserSerializer, ProfileSerializer
from rest_framework.response import Response
from .models import *
from .models import OneTimePassword
from .utils import send_code_to_user
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .forms import UserForms, LoginForms
from django.contrib import messages
from django.contrib import auth
from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from .permissions import IsPrivateAllowed
from moduler.models import ModulerModel, ModulerUserModel, ProfileModuler


# Create your views here.



class SignupUserView(GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        user_data = request.data
        print(user_data)
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            # send_code_to_user(user['email'])
            # send email function user['email']
            return Response({
                'data': user,
                'message': f"Hi {user['first_name']} thanks for signing up a sam"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otecode = request.data.get("otp")
        # print(otecode)
        try:
            user_code_obj = OneTimePassword.objects.get(code=otecode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    "message": "تم تسجيل الدخول بنجاح"
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "الكود غير صحيح تم التسجيل"
            }, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({
                "message": "الكود غير صحيح"
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        user = auth.authenticate(email=request.data["email"], password=request.data["password"])

        # print(user)
        # if request.user.is_anonymous:
        #     print("sam")
        #     print(request.data)
        #

        # else:
        # print(user)
        # if not user:
        # user_em = User.objects.get(id=user.manageid)
        # employee = UserEmployee.objects.filter(usermanager=user_em, time_finshe=False, user=user)
        # print(user)
        # if employee:
        #
        #     type_work = employee[0].type_work
        # else:
        #     type_work = ""


        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        # else:
        #     print("xxxxxxx")
        #
        #     return Response("انته مسجل دخول", status=status.HTTP_423_LOCKED)


class TestAuthView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.data["shop_name"])
        profile = Profile()
        profile.user = request.user
        profile.shop_name = request.data["shop_name"]
        profile.dec_name = request.data["dec_name"]
        profile.phone = request.data["phone"]
        profile.address = request.data["address"]
        profile.city = request.data["city"]
        profile.profile_picture = request.data["profile_picture"]
        profile.logo_picture = request.data["logo_picture"]
        profile.post_code = request.data["post_code"]
        profile.save()
        return Response({"profile is created"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        if user.manager:
            pass
            # print(user)
        else:
            # print(user)
            user = user.manageid
            # print(user.manageid)
        userProfile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(userProfile)

        user1 = serializer.data
        print(user1)
        return Response(user1, status=status.HTTP_200_OK)

############################################################

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response({"message": "تم ارسال الرابط الى ايميلك"}, status=status.HTTP_200_OK)

class PasswordResetConfrim(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message": "token is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"success": True, "message": "المعلومات غير صحيحه", "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({"message": "token is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "password rest successfull"}, status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutUserSerializer
    def post(self, request):
        # auth.logout(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)



def SignUp(request):
    if request.method == "POST" and "btnsignup" in request.POST:
        firstname = None
        lastname = None
        email = None
        password = None
        if "firstname" in request.POST:
            firstname = request.POST["firstname"]
        else:
            messages.error(request, "Error in first name")
        if "lastname" in request.POST:
            lastname = request.POST["lastname"]
        else:
            messages.error(request, "Error in last name")
        if "email" in request.POST:
            email = request.POST["email"]
        else:
            messages.error(request, "Error in  email")
        if "password" in request.POST:
            password = request.POST["password"]
        else:
            messages.error(request, "Error in password")

        if request.method == "POST":
            # add user## create_user
            user = User.objects.create_user(first_name=firstname, last_name=lastname,
                                            email=email, password=password)
            user.save()
            send_code_to_user(email)

            auth.login(request, user)
            return redirect("signin")
            # return render(request, "accounts/signin.html")
            # print(firstname)
    else:
        return render(request, "accounts/signup.html")


def signin(request):

    if request.method == "POST" and "btnlogin" in request.POST:
        # vars for failds
        email = None
        password = None

        # Get valuse from the form
        # model user
        if "email" in request.POST:
            email = request.POST["email"]
        else:
            messages.error(request, "Error in user name")
        if "password" in request.POST:
            password = request.POST["password"]
        else:
            messages.error(request, "Error in password")

        if email and password:

            user = auth.authenticate(email=email, password=password)
            # send_code_to_user(email)
            if user is not None:
                auth.login(request, user)

                return redirect("home")

            else:
                messages.error(request, "خطأ فى الايميل او الباسورد")

        else:
            messages.error(request, 'check empty fields')

        return redirect("signin")
    else:
        forms_user = LoginForms()

        context = {

            "formsuser": forms_user
        }
        return render(request, "accounts/signin.html", context)



def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('home')
# eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeevents


def prof(request):
    usermanage = UserManage.objects.get(user=request.user)
    modulerProf = ModulerUserModel.objects.filter(usermanage=usermanage)
    print(modulerProf[0])
    if request.method == "POST" and "btnsave" in request.POST:


        # vars for failds
        shopename = None
        shopedec = None
        address = None
        city = None
        phone = None
        postcode = None

        # Get valuse from the form
        # model user
        if "shopename" in request.POST:
            shopename = request.POST["shopename"]
        else:
            messages.error(request, "خطأ فى اسم المتجر")
        if "shopedec" in request.POST:
            shopedec = request.POST["shopedec"]
        else:
            messages.error(request, "خطأ فى وصف المتجر")
        if "address" in request.POST:
            address = request.POST["address"]
        else:
            messages.error(request, "خطأ فى العنوان")
        if "city" in request.POST:
            city = request.POST["city"]
        else:
            messages.error(request, "خطأ فى اسم المحافظه ")
        if "phone" in request.POST:
            phone = request.POST["phone"]
        else:
            messages.error(request, "خطأ فى رقم التليفون")
        if "postcode" in request.POST:
            postcode = request.POST["postcode"]
        else:
            messages.error(request, "خطأ فى رقم السجل التجارى")
        userprofile = ProfileModuler.objects.filter(modulerprofile=modulerProf[0])
        if userprofile:
            userprofile = ProfileModuler.objects.get(modulerprofile=modulerProf[0])
            userprofile.shop_name = shopename
            userprofile.dec_name = shopedec
            userprofile.phone = phone
            userprofile.address = address
            userprofile.city = city
            userprofile.profile_picture = request.FILES["imgprofile"]
            userprofile.logo_picture = request.FILES["logo"]
            userprofile.post_code = postcode
            userprofile.save()
            return redirect("prof")
            # print("xxxxxxxxxxx")
        else:
            print(request.POST)
            profile = ProfileModuler()

            profile.modulerprofile = modulerProf[0]
            profile.shop_name = shopename
            profile.dec_name = shopedec
            profile.phone = phone
            profile.address = address
            profile.city = city
            profile.profile_picture = request.FILES["imgprofile"]
            profile.logo_picture = request.FILES["logo"]
            profile.post_code = postcode
            profile.save()


            return render(request, "pages/dashbord.html")


    else:

        if not request.user.is_anonymous:
            userprofile = ProfileModuler.objects.filter(modulerprofile=modulerProf[0])
            if userprofile:
                userprofile = ProfileModuler.objects.get(modulerprofile=modulerProf[0])
                # userManage = UserManage.objects.get(modulerprofile=modulerProf[0])
                # print(settings.MEDIA_ROOT)
                context = {
                    # "pp": settings.MEDIA_ROOT+"\images\store-logo.png",
                    "shopename": userprofile.shop_name,
                    "shopedec": userprofile.dec_name,
                    "address": userprofile.address,
                    "address2": f"{userprofile.city}  {userprofile.address}",
                    "num_product": f"{2}",
                    "num_emp": usermanage.num_employee,

                    "phone": userprofile.phone,
                    "city": userprofile.city,
                    "profile_picture": userprofile.logo_picture,
                    "email": request.user.email,
                    "postcode": userprofile.post_code,
                    "username": request.user.get_full_name,
                    "firstname": request.user.first_name,
                    "lastname": request.user.last_name,
                }
                return render(request, "pages/admin.html", context)
            else:
                return render(request, "accounts/profile.html")
                # return redirect("profile")
        else:
            return redirect("signin")

            # return redirect("profile")
        # return redirect("signin")



@api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def profileemp(request):
    if request.user.is_authenticated:
        firstname = request.data["first_name"]
        lastname = request.data["last_name"]
        email = request.data["email"]
        password = request.data["password"]
        user_emp = User.objects.get(id=request.data["id"])
        print(user_emp)
        user_emp.first_name = firstname
        user_emp.last_name = lastname
        user_emp.email = email

        if not password.startswith('pbkdf2_sha256$'):
            user_emp.set_password(password)
        user_emp.save()

        return Response("انته مش مدير", status=status.HTTP_201_CREATED)



