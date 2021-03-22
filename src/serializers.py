from rest_framework import serializers
from adminpanel.models import User
from .models import AppUser, Settings, UserSearch, Booking, GeneralInquiry


class UserCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    password = serializers.CharField(style={'input_type': 'password'})
    confirm_password = serializers.CharField(style={'input_type': 'password'})
    referral_code = serializers.CharField(required=False)
    device_token = serializers.CharField()
    device_type = serializers.CharField()
    language = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'full_name', 'country_code', 'phone_number', 'referral_code', 'language', 'device_token','device_type', 'password',
            'confirm_password')


class LoginSerializer(serializers.ModelSerializer):
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    device_token = serializers.CharField()
    device_type = serializers.CharField()
    language = serializers.CharField()

    class Meta:
        model = User
        fields = ('country_code', 'phone_number', 'device_token','device_type', 'language')


class CheckUserSerializer(serializers.ModelSerializer):
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('country_code', 'phone_number')


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField()

    class Meta:
        model = AppUser
        fields = ('profile_pic',)


class UpdateUserLanguageSerializer(serializers.ModelSerializer):
    language = serializers.CharField()

    class Meta:
        model = Settings
        fields = ('language',)


class UserSearchSerializer(serializers.ModelSerializer):
    searched_value = serializers.CharField()

    class Meta:
        model = UserSearch
        fields = ('searched_value',)


class BookingSerializer(serializers.ModelSerializer):
    service = serializers.CharField()
    requirement = serializers.CharField()
    service_provider = serializers.CharField()
    date = serializers.CharField()
    time = serializers.CharField()
    address = serializers.CharField()
    building = serializers.CharField()
    city = serializers.CharField()
    landmark = serializers.CharField()
    status = serializers.CharField()
    sub_total = serializers.FloatField()
    fees = serializers.FloatField()
    discount = serializers.FloatField()
    total = serializers.FloatField()
    default_address = serializers.BooleanField()

    class Meta:
        model = Booking
        fields = (
            'service', 'service_provider', 'date', 'time', 'requirement', 'address', 'building', 'city', 'landmark',
            'status', 'sub_total', 'fees', 'discount', 'total', 'default_address')


class BookingDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Booking
        fields = ('id',)


class GeneralInquirySerializer(serializers.ModelSerializer):
    order = serializers.CharField()
    subject = serializers.CharField()
    message = serializers.CharField()
    image_1 = serializers.FileField()
    image_2 = serializers.FileField()

    class Meta:
        model = GeneralInquiry
        fields = ('order', 'subject', 'message', 'image_1', 'image_2')
