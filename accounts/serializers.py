from rest_framework import serializers

from employee.models import UserEmployee
from employee.serializers import UserEmployeeSerializer
from moduler.serializer import MoudulerUserSerializer
from .models import *
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=100, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',            
            'email',

            'password',
            'password2',
        ]
        # read_only_field = ['id', 'photo_url',]
        
    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("password do not match")
        # request = self.context.get('request')
        # if request.method == "POST":
        #     if User.objects.filter(email__iexact=email).exists():
        #         return serializers.ValidationError('Email already exist! Please, try another email')
        return attrs
    
    def create(self, validated_data):


        user = User.objects.create_user(
        first_name=validated_data.get('first_name'),
        last_name=validated_data.get('last_name'),
        email=validated_data['email'],

        password=validated_data.get('password')
        )
        # user.set_password(validated_data['password'])
        # user.save()
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=120, required=True, min_length=3)
    password = serializers.CharField(max_length=100, required= True,style={'input_type': 'password'},write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, min_length=5, read_only=True)
    refresh_token = serializers.CharField(max_length=255, min_length=5, read_only=True)
    isEmp= serializers.BooleanField(read_only=True)
    to_moduler = serializers.IntegerField(read_only=True)
    type_work = serializers.CharField(max_length=255, min_length=5, read_only=True)

    class Meta:
        model = User
        fields = ['id', "password", 'email', "full_name", 'access_token', 'refresh_token', "isEmp", "to_moduler", "type_work"]
        read_only_fields    = ['access_token', 'refresh_token', "first_name"]


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get("request")
        user = authenticate(request, email=email, password=password)
        user_em = User.objects.get(id=user.manageid)
        employee = UserEmployee.objects.filter(usermanager=user_em, time_finshe=False, user=user)


        if employee:

            to_moduler = employee[0].to_moduler
            type_work = employee[0].type_work
        else:
            to_moduler = 0
            type_work = user.get_full_name

        # print(type_work)
        if not user:
            raise AuthenticationFailed("المعلومات غير صالحه حاول مره اخره")
        if not user.is_verified:
            raise AuthenticationFailed("غير مسجل")
        user_tokens = user.tokens()

        return {
            "type_work": type_work,
            "to_moduler": to_moduler,
            'isEmp': user.emp,
            "email": user.email,
            "full_name": user.get_full_name,
            "access_token": str(user_tokens.get("access")),
            "refresh_token": str(user_tokens.get("refresh")),
        }



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=120)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get("request")
            site_domain = get_current_site(request).domain
            relative_link = reverse("password-reset-confirm", kwargs={"uidb64": uidb64, "token": token})
            abslink = f"http//{site_domain}{relative_link}"
            email_body = f"روح هات الباسوورد \n{abslink}"
            print(email)
            print(email_body)
            data = {
                "email_body": email_body,
                "email_subject": "Reset your password",
                "to_email": user.email
            }
            send_normal_email(data)
        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):
        try:
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            password = attrs.get("password")
            confirm_password = attrs.get("confirm_password")
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("rest link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")



class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    default_error_messages = {
        "bad_token": ("token is invalid or has expired")
    }

    def validate(self, attrs):
        self.token = attrs.get("refresh_token")
        return attrs
    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail("bad_token")

class UserSerializer(serializers.ModelSerializer):
    userman = serializers.SerializerMethodField(method_name="get_user_manage", read_only=True)
    useremp = serializers.SerializerMethodField(method_name="get_employee", read_only=True)
    # profile = serializers.SerializerMethodField(method_name="get_user_profile", read_only=True)
    class Meta:
        model = User
        fields = "__all__"

    def get_user_manage(self, obj):
        user_manage = obj.usermanage

        serializer = UserManageSerializer(user_manage)
        return serializer.data
    def get_employee(self, obj):

        user_emp = obj.employeemanager

        serializer = UserEmployeeSerializer(user_emp, many=True)
        return serializer.data

    # def get_user_profile(self, obj):
    #     user_emp = obj.userprofile
    #
    #     serializer = ProfileSerializer(user_emp)
    #     return serializer.data




class UserESerializer(serializers.ModelSerializer):
    # userman = serializers.SerializerMethodField(method_name="get_user_manage", read_only=True)
    user_emp = serializers.SerializerMethodField(method_name="get_employee", read_only=True)
    # profile = serializers.SerializerMethodField(method_name="get_user_profile", read_only=True)
    class Meta:
        model = User
        fields = "__all__"

    # def get_user_manage(self, obj):
    #     user_manage = obj.usermanage
    #
    #     serializer = UserManageSerializer(user_manage)
    #     return serializer.data
    def get_employee(self, obj):

        user_emp = obj.employeeuser.filter(time_finshe=False)

        serializer = UserEmployeeSerializer(user_emp, many=True)
        return serializer.data

    # def get_user_profile(self, obj):
    #     user_emp = obj.userprofile
    #
    #     serializer = ProfileSerializer(user_emp)
    #     return serializer.data




class UserManageSerializer(serializers.ModelSerializer):
    mymodulers = serializers.SerializerMethodField(method_name="get_modulers", read_only=True)

    class Meta:
        model = UserManage
        fields = "__all__"


    def get_modulers(self, obj):
        user_emp = obj.mymodulers

        serializer = MoudulerUserSerializer(user_emp, many=True)
        return serializer.data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"



class XSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"