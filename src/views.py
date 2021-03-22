from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import UserCreateSerializer, LoginSerializer, CheckUserSerializer, UpdateUserProfileSerializer, \
    UpdateUserLanguageSerializer, UserSearchSerializer, BookingSerializer, BookingDetailSerializer, \
    GeneralInquirySerializer, UpdateOrderStatusSerializer, RatingAndReviewsSerializer
from .models import AppUser, Settings, UserSearch, Booking, TermsAndCondition, ContactUs, PrivacyPolicy, GeneralInquiry, \
    AboutUs, RatingReview, OffersAndDiscount
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from adminpanel.models import User, Services, TopServices, ServiceProvider


class CreateUser(APIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=self.request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            phone_number = serializer.validated_data['phone_number']
            full_name = serializer.validated_data['full_name']
            country_code = serializer.validated_data['country_code']
            # password = serializer.validated_data['password']
            # confirm_password = serializer.validated_data['confirm_password']
            referral_code = serializer.validated_data.get('referral_code' or None)
            device_token = serializer.validated_data['device_token']
            device_type = serializer.validated_data['device_type']
            language = serializer.validated_data['language']
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            try:
                User.objects.get(phone_number=phone_number)
                return Response({'message': 'User with this number already exists', 'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                print(e)
                # if password == confirm_password:
                user = User.objects.create(full_name=full_name, email=str(phone_number) + '@email.com',
                                           country_code=country_code, phone_number=phone_number)
                user.set_password('Test@123')
                app_user = AppUser.objects.create(user=user, full_name=full_name, referral_code=referral_code,
                                                  device_token=device_token, device_type=device_type, lat=lat,
                                                  long=long)
                app_user_settings = Settings.objects.get(user=app_user)
                app_user_settings.language = language
                app_user_settings.save()
                token = Token.objects.get_or_create(user=user)
                return Response({'message': 'User created successfully', 'id': app_user.id, 'token': token[0].key,
                                 'full_name': app_user.full_name, 'country_code': user.country_code,
                                 'phone_number': user.phone_number, 'status': HTTP_200_OK})
                # else:
                #     return Response(
                #         {'message': 'Password and Confirm password do not match', 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=self.request.data)
        if serializer.is_valid():
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            device_token = serializer.validated_data['device_token']
            device_type = serializer.validated_data['device_type']
            language = serializer.validated_data['language']
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            try:
                user_obj = User.objects.get(country_code=country_code, phone_number=phone_number)
                user_id = AppUser.objects.get(user=user_obj)
                settings_obj = Settings.objects.get(user=user_id)
                settings_obj.language = language
                settings_obj.save()
                existing_token = Token.objects.get(user=user_obj)
                existing_token.delete()
                token = Token.objects.get_or_create(user=user_obj)
                user_device_token = user_id.device_token
                print('previous token ', user_device_token)
                user_id.device_token = device_token
                user_id.device_type = device_type
                user_id.long = long
                user_id.lat = lat
                user_id.save(update_fields=['device_token', 'device_type', 'long', 'lat'])
                print('updated device token ', user_id.device_token)
                token = token[0]
                return Response({'token': token.key, 'id': user_id.id, 'country_code': user_obj.country_code,
                                 'phone_number': user_obj.phone_number, 'status': HTTP_200_OK, 'lat': user_id.lat,
                                 'long': user_id.long})
            except Exception as e:
                print(e)
                try:
                    user_obj = User.objects.get(country_code=country_code, phone_number=phone_number)
                    user_id = AppUser.objects.get(user=user_obj)
                    settings_obj = Settings.objects.get(user=user_id)
                    settings_obj.language = language
                    settings_obj.save()
                    token = Token.objects.get_or_create(user=user_obj)
                    user_device_token = user_id.device_token
                    print('previous token ', user_device_token)
                    user_id.device_token = device_token
                    user_id.device_type = device_type
                    user_id.lat = lat
                    user_id.long = long
                    user_id.save(update_fields=['device_token', 'device_type', 'lat', 'long'])
                    print('updated device token ', user_id.device_token)
                    token = token[0]
                    return Response({'token': token.key, 'id': user_id.id, 'country_code': user_obj.country_code,
                                     'phone_number': user_obj.phone_number, 'status': HTTP_200_OK, 'lat': user_id.lat,
                                     'long': user_id.long})
                except Exception as e:
                    return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class CheckUserExists(APIView):
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = CheckUserSerializer(data=self.request.data)
        if serializer.is_valid():
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            try:
                User.objects.get(country_code=country_code, phone_number=phone_number)
                return Response({'message': True, 'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': False, 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class UpdateUserProfile(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UpdateUserProfileSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        try:
            app_user = AppUser.objects.get(user=user)
            serializer = UpdateUserProfileSerializer(data=self.request.data)
            if serializer.is_valid():
                profile_pic = serializer.validated_data['profile_pic']
                print(profile_pic)
                app_user.profile_pic = profile_pic
                app_user.save()
                return Response({'message': 'Profile updated successfully', 'status': HTTP_200_OK})
            else:
                return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class GetUserProfilePic(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        try:
            app_user = AppUser.objects.get(user=user)
            return Response(
                {'message': 'Fetched app user profile pic successfully', 'profile_pic': app_user.profile_pic.url,
                 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class UpdateUserLanguage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserLanguageSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UpdateUserLanguageSerializer(data=self.request.data)
        if serializer.is_valid():
            try:
                language = serializer.validated_data['language']
                app_user = AppUser.objects.get(user=user)
                settings_obj = Settings.objects.get(user=app_user)
                settings_obj.language = language
                settings_obj.save()
                return Response({'message': 'Language updated successfully', 'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class HomeView(APIView):
    model = Services
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        services = Services.objects.all()
        top_services = TopServices.objects.all()
        top_services_list = []
        for object in top_services:
            top_services_list.append(
                {'id': object.service.id, 'service_name': object.service.service_name,
                 'image_1': object.service.image_1.url,
                 'image_2': object.service.image_2.url})
        return Response({'services': services.values(), 'top_services': top_services_list, 'status': HTTP_200_OK})


class SearchingServices(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        searched_value = self.request.query_params.get('search')
        services = Services.objects.filter(service_name__icontains=searched_value)
        print(services)
        service_providers = ServiceProvider.objects.filter(services__service_name__icontains=searched_value)
        return Response(
            {'services': services.values(), 'service_providers': service_providers.values(), 'status': HTTP_200_OK})


class SaveSearchesHistory(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSearchSerializer
    model = UserSearch

    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        try:
            app_user = AppUser.objects.get(user=user)
            print(app_user)
            serializer = UserSearchSerializer(data=self.request.data)
            if serializer.is_valid():
                searched_value = serializer.validated_data['searched_value']
                UserSearch.objects.create(
                    user=app_user,
                    searched_value=searched_value
                )
                return Response({"message": "Searches saved successfully", 'status': HTTP_200_OK})
            else:
                return Response({'messages': serializer.errors, 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class GetUserPastSearches(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserSearch

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        past_searches = UserSearch.objects.filter(user=app_user)
        return Response({'data': past_searches.values(), 'status': HTTP_200_OK})


class BookingView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking
    serializer_class = BookingSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        serializer = BookingSerializer(data=self.request.data)
        if serializer.is_valid():
            try:
                requirement = serializer.validated_data['requirement']
                service = serializer.validated_data['service']
                service_provider = serializer.validated_data['service_provider']
                date = serializer.validated_data['date']
                time = serializer.validated_data['time']
                address = serializer.validated_data['address']
                building = serializer.validated_data['building']
                city = serializer.validated_data['city']
                landmark = serializer.validated_data['landmark']
                status = serializer.validated_data['status']
                default_address = serializer.validated_data['default_address']
                sub_total = serializer.validated_data['sub_total']
                fees = serializer.validated_data['fees']
                discount = serializer.validated_data['discount']
                total = serializer.validated_data['total']
                booking = Booking.objects.create(
                    user=app_user,
                    requirement=requirement,
                    service=Services.objects.get(id=service),
                    service_provider=ServiceProvider.objects.get(id=service_provider),
                    date=date,
                    time=time,
                    address=address,
                    building=building,
                    city=city,
                    landmark=landmark,
                    status=status,
                    sub_total=sub_total,
                    fees=fees,
                    discount=discount,
                    total=total,
                    default_address=default_address
                )
                return Response(
                    {'message': 'Service booked successfully', 'booking': booking.id, 'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class GetBookingDetail(APIView):
    model = Booking
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = BookingDetailSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        # booking_id = self.request.query_params.get('booking_id')
        serializer = BookingDetailSerializer(data=self.request.data)
        if serializer.is_valid():
            booking_id = serializer.validated_data['id']
            # print(serializer.validated_data.get('id'))
            # booking_id = serializer.validated_data.get('id')
            try:
                booking = Booking.objects.get(user=app_user, id=booking_id)
                return Response(
                    {'id': booking.id, 'service_id': booking.service.id, 'service_name': booking.service.service_name,
                     'service_provider_id': booking.service_provider.full_name, 'booking_date': booking.date,
                     'booking_time': booking.time, 'address': booking.address, 'building': booking.building,
                     'city': booking.city, 'landmark': booking.landmark, 'default_address': booking.default_address,
                     'booking_status': booking.status, 'sub_total': booking.sub_total, 'fees': booking.fees,
                     'discount': booking.discount, 'total': booking.total, 'requirement': booking.requirement,
                     'booked_at': booking.created_at,
                     'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_200_OK})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class ContactUsView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ContactUs

    def get(self, request, *args, **kwargs):
        return Response(
            {'phone_number': ContactUs.objects.all().first().phone_number,
             'email': ContactUs.objects.all().first().email, 'status': HTTP_200_OK})


class PrivacyPolicyView(APIView):
    model = PrivacyPolicy

    def get(self, request, *args, **kwargs):
        return Response({'policy': PrivacyPolicy.objects.all().first().policy,
                         'policy_arabic': PrivacyPolicy.objects.all().first().policy_arabic, 'status': HTTP_200_OK})


class TermsAndConditionView(APIView):
    model = TermsAndCondition

    def get(self, request, *args, **kwargs):
        return Response({'terms': TermsAndCondition.objects.all().first().terms,
                         'terms_arabic': TermsAndCondition.objects.all().first().terms_arabic,
                         'status': HTTP_200_OK})


class AboutUsView(APIView):
    model = AboutUs

    def get(self, request, *args, **kwargs):
        return Response({'content': AboutUs.objects.all().first().content,
                         'content_arabic': AboutUs.objects.all().first().content_arabic, 'status': HTTP_200_OK})


class GeneralInquiryView(APIView):
    model = GeneralInquiry
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = GeneralInquirySerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        serializer = GeneralInquirySerializer(data=self.request.data)
        if serializer.is_valid():
            order = serializer.validated_data['order']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            image_1 = serializer.validated_data['image_1']
            image_2 = serializer.validated_data['image_2']
            try:
                GeneralInquiry.objects.create(
                    user=app_user,
                    order=Booking.objects.get(id=order),
                    subject=subject,
                    message=message,
                    image_1=image_1,
                    image_2=image_2
                )
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
            return Response({'message': 'Inquiry form submitted successfully', 'status': HTTP_200_OK})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        app_user.device_token = ''
        app_user.save()
        request.user.auth_token.delete()
        return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})


class UpdateOrderStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateOrderStatusSerializer
    model = Booking

    def patch(self, request, *args, **kwargs):
        order_id = self.request.POST['id']
        status = self.request.POST['status']
        order_obj = Booking.objects.get(id=order_id)
        order_obj.status = status
        order_obj.save()
        return Response({'message': 'Order updated successfully', 'status': HTTP_200_OK})


class UpcomingBooking(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        order_obj = Booking.objects.filter(status='Started')
        orders = []
        for obj in order_obj:
            orders.append({'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                           'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time})
        return Response({'data': orders, 'status': HTTP_200_OK})


class PastBooking(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        order_obj = Booking.objects.filter(status='Completed')
        orders = []
        for obj in order_obj:
            orders.append({'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                           'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time})
        return Response({'data': orders, 'status': HTTP_200_OK})


class OnGoingBooking(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    model = Booking

    def get(self, request, *args, **kwargs):
        order_obj = Booking.objects.filter(status='Accepted')
        orders = []
        for obj in order_obj:
            orders.append({'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                           'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time})
        return Response({'data': orders, 'status': HTTP_200_OK})


class RatingAndReviews(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RatingReview
    serializer_class = RatingAndReviewsSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        print(self.request.POST)
        serializer = RatingAndReviewsSerializer(data=self.request.data)
        if serializer.is_valid():
            order = serializer.validated_data['id']
            reviews = serializer.validated_data['review']
            rating = serializer.validated_data['rating']
            RatingReview.objects.create(user=app_user, order=Booking.objects.get(id=order), reviews=reviews,
                                        rating=rating)
            return Response({'message': 'Rating submitted successfully', 'status': HTTP_200_OK})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class GetServiceReviewRatings(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RatingReview

    def get(self, request, *args, **kwargs):
        service_id = self.request.query_params.get('service_id')
        try:
            rating_obj = RatingReview.objects.filter(order__service__id=service_id)
            ratings = []
            for obj in rating_obj:
                if obj.user.profile_pic:
                    ratings.append(
                        {'user_name': obj.user.full_name, 'user_image': obj.user.profile_pic.url, 'rating': obj.rating,
                         'review': obj.reviews})
                else:
                    ratings.append(
                        {'user_name': obj.user.full_name, 'user_image': '', 'rating': obj.rating,
                         'review': obj.reviews})
            return Response({'rating_count': len(rating_obj), 'data': ratings, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class GetDefaultOfferPercentView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = OffersAndDiscount

    def get(self, request, *args, **kwargs):
        return Response({'percent': OffersAndDiscount.objects.all()[0].percent, 'status': HTTP_200_OK})


class GetAllOffersAndDiscount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = OffersAndDiscount

    def get(self, request, *args, **kwargs):
        offers_obj = OffersAndDiscount.objects.all()
        offers = []
        for obj in offers_obj:
            offers.append({'coupon_code': obj.coupon_code, 'percent': obj.percent})
        return Response({'data': offers, 'status': HTTP_200_OK})
