from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import UserCreateSerializer, LoginSerializer, CheckUserSerializer, UpdateUserProfileSerializer, \
    UpdateUserLanguageSerializer, UserSearchSerializer, BookingSerializer, BookingDetailSerializer, \
    GeneralInquirySerializer, UpdateOrderStatusSerializer, RatingAndReviewsSerializer, InquirySerializer, \
    ServiceProviderLoginSerializer, ForgetPasswordSerializer, NewBookingRequestDetailSerializer, \
    UpdateBookingByServiceProviderSerializer, ProviderRegistrationSerializer
from .models import AppUser, Settings, UserSearch, Booking, TermsAndCondition, ContactUs, PrivacyPolicy, GeneralInquiry, \
    AboutUs, RatingReview, OffersAndDiscount, UserNotification, Inquiry, ProviderRegistration
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from adminpanel.models import User, Services, TopServices, ServiceProvider, Category, AdminNotifications, SubCategory


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
            lang = serializer.validated_data['lang']
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
                                                  lang=lang)
                app_user_settings = Settings.objects.get(user=app_user)
                app_user_settings.language = language
                app_user_settings.save()
                token = Token.objects.get_or_create(user=user)
                AdminNotifications.objects.create(
                    user=User.objects.get(email='admin@email.com'),
                    title='New User Registration',
                    body='A new user has registered on the platform'
                )
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
            lang = serializer.validated_data['lang']
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
                user_id.lang = lang
                user_id.lat = lat
                user_id.save(update_fields=['device_token', 'device_type', 'lang', 'lat'])
                print('updated device token ', user_id.device_token)
                token = token[0]
                return Response({'token': token.key, 'id': user_id.id, 'full_name': user_id.full_name,
                                 'country_code': user_obj.country_code,
                                 'phone_number': user_obj.phone_number, 'status': HTTP_200_OK, 'lat': user_id.lat,
                                 'lang': user_id.lang})
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
                    user_id.lang = lang
                    user_id.save(update_fields=['device_token', 'device_type', 'lat', 'lang'])
                    print('updated device token ', user_id.device_token)
                    token = token[0]
                    return Response({'token': token.key, 'id': user_id.id, 'country_code': user_obj.country_code,
                                     'phone_number': user_obj.phone_number, 'status': HTTP_200_OK, 'lat': user_id.lat,
                                     'lang': user_id.lang})
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
                UserNotification.objects.create(user=app_user, title='Profile pic update',
                                                body='Your profile pic has been updated successfully')
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

    # from rest_framework.throttling import UserRateThrottle
    # throttle_classes = [UserRateThrottle]
    # @method_decorator(cache_page(60 * 60 * 2))

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_id = AppUser.objects.get(user=user)
        service_list = []
        category_list = []
        services = Services.objects.all()
        categories = Category.objects.all()
        for category in categories:
            if category.category_image:
                category_list.append({'id': category.id, 'category_name': category.category_name,
                                      'category_image': category.category_image.url})
            else:
                category_list.append({'id': category.id, 'category_name': category.category_name,
                                      'category_image': ''})
        for service in services:
            service_list.append(
                {'id': service.id, 'category_id': service.category.id, 'sub_category_id': service.sub_category.id,
                 'service_name': service.service_name, 'field_1': service.field_1,
                 'field_2': service.field_2, 'field_3': service.field_3, 'field_4': service.field_4,
                 'base_price': service.base_price, 'image_1': service.image_1.url, 'image_2': service.image_2.url})
        top_services = TopServices.objects.all()
        top_services_list = []
        for object in top_services:
            top_services_list.append(
                {'id': object.service.id, 'service_name': object.service.service_name,
                 'image_1': object.service.image_1.url,
                 'image_2': object.service.image_2.url})
        return Response({'services': service_list, 'top_services': top_services_list,
                         'categories': category_list, 'status': HTTP_200_OK, 'lat': user_id.lat, 'long': user_id.lang})


class GetSubCategory(APIView):
    model = Category
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        category = self.request.query_params.get('category')
        print(category)
        sub_categories = SubCategory.objects.filter(category=category)
        sub_categories_list = []
        for sub_category in sub_categories:
            if sub_category.sub_category_image:
                sub_categories_list.append({'id': sub_category.id, 'category_id': sub_category.category.id,
                                            'sub_category_name': sub_category.sub_category_name,
                                            'sub_category_image': sub_category.sub_category_image
                                           .url})
            else:
                sub_categories_list.append({'id': sub_category.id, 'category_id': sub_category.category.id,
                                            'sub_category_name': sub_category.sub_category_name,
                                            'sub_category_image': ''})
        return Response({'data': sub_categories_list, 'status': HTTP_200_OK})


class GetServices(APIView):
    model = Services
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        sub_category = self.request.query_params.get('sub_category')
        services = Services.objects.filter(sub_category=sub_category)
        service_list = []
        for service in services:
            ratings_obj = RatingReview.objects.filter(order__service=service.id).count()
            ratings = 0
            for obj in RatingReview.objects.filter(order__service=service.id):
                ratings += obj.rating
            try:
                average_ratings = ratings / ratings_obj
            except Exception as e:
                average_ratings = 0
            service_list.append(
                {'id': service.id, 'category_id': service.category.id, 'sub_category_id': service.sub_category.id,
                 'service_name': service.service_name, 'field_1': service.field_1,
                 'field_2': service.field_2, 'field_3': service.field_3, 'field_4': service.field_4,
                 'base_price': service.base_price, 'image_1': service.image_1.url, 'image_2': service.image_2.url,
                 'average_ratings': average_ratings, 'reviews': ratings_obj})
        return Response({'data': service_list, 'status': HTTP_200_OK})


class GetServiceDetail(APIView):
    model = Services
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        try:
            service_obj = Services.objects.get(id=id)
            # ratings_obj = Booking.objects.filter(service=id).count()
            ratings_obj = RatingReview.objects.filter(order__service=id).count()
            ratings = 0
            for obj in RatingReview.objects.filter(order__service=id):
                ratings += obj.rating
            try:
                average_ratings = ratings / ratings_obj
            except Exception as e:
                average_ratings = 0
            return Response({'service_id': service_obj.id, 'service_name': service_obj.service_name,
                             'field_1': service_obj.field_1, 'field_2': service_obj.field_2,
                             'field_3': service_obj.field_3,
                             'field_4': service_obj.field_4, 'base_price': service_obj.base_price,
                             'image_1': service_obj.image_1.url, 'image_2': service_obj.image_2.url,
                             'status': HTTP_200_OK,
                             'rating_count': ratings_obj, 'average_rating': average_ratings})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class SearchingServices(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        searched_value = self.request.query_params.get('search')
        try:
            services = Services.objects.filter(
                Q(category__category_name__icontains=searched_value.lower()) | Q(
                    service_name__icontains=searched_value.lower()))
            print(services)
            # categories = Category.objects.filter(category_name__icontains=searched_value)
            categories = []
            service_list = []
            for service_obj in services:
                ratings_obj = RatingReview.objects.filter(order__service=service_obj.id).count()
                ratings = 0
                for obj in RatingReview.objects.filter(order__service=service_obj.id):
                    ratings += obj.rating
                try:
                    average_ratings = ratings / ratings_obj
                except Exception as e:
                    average_ratings = 0
                service_list.append({'service_id': service_obj.id, 'service_name': service_obj.service_name,
                                     'field_1': service_obj.field_1, 'field_2': service_obj.field_2,
                                     'field_3': service_obj.field_3,
                                     'field_4': service_obj.field_4, 'base_price': service_obj.base_price,
                                     'image_1': service_obj.image_1.url, 'image_2': service_obj.image_2.url,
                                     'status': HTTP_200_OK,
                                     'rating_count': ratings_obj, 'average_rating': average_ratings})
            for service in services:
                c = service.category.id
                ratings_obj = RatingReview.objects.filter(order__service=service.id).count()
                ratings = 0
                for obj in RatingReview.objects.filter(order__service=service.id):
                    ratings += obj.rating
                try:
                    average_ratings = ratings / ratings_obj
                except Exception as e:
                    average_ratings = 0
                if Category.objects.get(id=c).category_image:
                    categories.append(
                        {'id': Category.objects.get(id=c).id,
                         'category_name': Category.objects.get(id=c).category_name,
                         'category_image': Category.objects.get(id=c).category_image.url,
                         'average_ratings': average_ratings, 'service_id': service.id,
                         'service_name': service.service_name, 'reviews_count': ratings_obj})
                else:
                    categories.append(
                        {'id': Category.objects.get(id=c).id,
                         'category_name': Category.objects.get(id=c).category_name,
                         'category_image': '', 'service_id': service.id,
                         'service_name': service.service_name, 'average_ratings': average_ratings,
                         'reviews_count': ratings_obj})
            service_providers = ServiceProvider.objects.filter(services__service_name__icontains=searched_value)
            return Response(
                {'services': service_list, 'service_providers': service_providers.values(),
                 'categories': categories, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


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
                try:
                    UserSearch.objects.get(searched_value=searched_value.lower())
                    return Response({"message": "Searches saved successfully", 'status': HTTP_200_OK})
                except Exception as e:
                    print(e)
                    UserSearch.objects.create(
                        user=app_user,
                        searched_value=searched_value.lower()
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
                # service_provider = serializer.validated_data['service_provider']
                date = serializer.validated_data['date']
                time = serializer.validated_data['time']
                address = serializer.validated_data['address']
                # building = serializer.validated_data['building']
                # city = serializer.validated_data['city']
                # landmark = serializer.validated_data['landmark']
                status = serializer.validated_data['status']
                default_address = serializer.validated_data['default_address']
                # sub_total = serializer.validated_data['sub_total']
                # fees = serializer.validated_data['fees']
                # discount = serializer.validated_data['discount']
                # total = serializer.validated_data['total']
                night_booking = serializer.validated_data['night_booking']
                if night_booking:
                    booking = Booking.objects.create(
                        user=app_user,
                        requirement=requirement,
                        service=Services.objects.get(id=service),
                        # service_provider=ServiceProvider.objects.get(id=service_provider),
                        date=date,
                        time=time,
                        address=address,
                        # building=building,
                        # city=city,
                        # landmark=landmark,
                        status=status,
                        # sub_total=sub_total,
                        fees=100,
                        # discount=discount,
                        total=total,
                        default_address=default_address,
                        night_booking=night_booking
                    )
                else:
                    booking = Booking.objects.create(
                        user=app_user,
                        requirement=requirement,
                        service=Services.objects.get(id=service),
                        # service_provider=ServiceProvider.objects.get(id=service_provider),
                        date=date,
                        time=time,
                        address=address,
                        # building=building,
                        # city=city,
                        # landmark=landmark,
                        status=status,
                        # sub_total=sub_total,
                        # fees=fees,
                        # discount=discount,
                        total=total,
                        default_address=default_address,
                        night_booking=night_booking
                    )
                AdminNotifications.objects.create(
                    user=User.objects.get(email='admin@email.com'),
                    title='New Booking Request',
                    body='A new service booking request has been placed on the platform'
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
                try:
                    if booking.promocode_applied:
                        return Response(
                            {'id': booking.id, 'service_id': booking.service.id,
                             'service_name': booking.service.service_name, 'quote': booking.quote,
                             'service_provider_name': booking.service_provider.full_name, 'booking_date': booking.date,
                             'booking_time': booking.time, 'address': booking.address,
                             'default_address': booking.default_address,
                             'booking_status': booking.status, 'sub_total': booking.sub_total, 'fees': booking.fees,
                             'discount': booking.discount, 'total': booking.total, 'requirement': booking.requirement,
                             'image_1': booking.service.image_1.url, 'image_2': booking.service.image_2.url,
                             'booked_at': booking.created_at,
                             'promocode_id': OffersAndDiscount.objects.get(coupon_code=booking.promocode).id,
                             'promocode_name': booking.promocode,
                             'promocode_status': booking.promocode_applied,
                             'status': HTTP_200_OK})
                    else:
                        return Response(
                            {'id': booking.id, 'service_id': booking.service.id,
                             'service_name': booking.service.service_name, 'quote': booking.quote,
                             'service_provider_name': booking.service_provider.full_name, 'booking_date': booking.date,
                             'booking_time': booking.time, 'address': booking.address,
                             'default_address': booking.default_address,
                             'booking_status': booking.status, 'sub_total': booking.sub_total, 'fees': booking.fees,
                             'discount': booking.discount, 'total': booking.total, 'requirement': booking.requirement,
                             'image_1': booking.service.image_1.url, 'image_2': booking.service.image_2.url,
                             'booked_at': booking.created_at,
                             'promocode_id': '',
                             'promocode_name': booking.promocode,
                             'promocode_status': booking.promocode_applied,
                             'status': HTTP_200_OK})
                except Exception as e:
                    if booking.promocode_applied:
                        return Response(
                            {'id': booking.id, 'service_id': booking.service.id,
                             'service_name': booking.service.service_name, 'quote': booking.quote,
                             'service_provider_id': '', 'booking_date': booking.date,
                             'booking_time': booking.time, 'address': booking.address,
                             'default_address': booking.default_address,
                             'booking_status': booking.status, 'sub_total': booking.sub_total, 'fees': booking.fees,
                             'discount': booking.discount, 'total': booking.total, 'requirement': booking.requirement,
                             'image_1': booking.service.image_1.url, 'image_2': booking.service.image_2.url,
                             'booked_at': booking.created_at,
                             'promocode_id': OffersAndDiscount.objects.get(coupon_code=booking.promocode).id,
                             'promocode_name': booking.promocode,
                             'promocode_status': booking.promocode_applied,
                             'status': HTTP_200_OK})
                    else:
                        return Response(
                            {'id': booking.id, 'service_id': booking.service.id,
                             'service_name': booking.service.service_name, 'quote': booking.quote,
                             'service_provider_id': '', 'booking_date': booking.date,
                             'booking_time': booking.time, 'address': booking.address,
                             'default_address': booking.default_address,
                             'booking_status': booking.status, 'sub_total': booking.sub_total, 'fees': booking.fees,
                             'discount': booking.discount, 'total': booking.total, 'requirement': booking.requirement,
                             'image_1': booking.service.image_1.url, 'image_2': booking.service.image_2.url,
                             'booked_at': booking.created_at,
                             'promocode_id': '',
                             'promocode_name': booking.promocode,
                             'promocode_status': booking.promocode_applied,
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
    """Privacy policy api"""
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


class InquiryView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = InquirySerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        serializer = InquirySerializer(data=self.request.data)
        if serializer.is_valid():
            service = serializer.validated_data['service']
            try:
                service_obj = Services.objects.get(id=service)
                subject = serializer.validated_data['subject']
                message = serializer.validated_data['message']
                image_1 = serializer.validated_data['image_1']
                image_2 = serializer.validated_data['image_2']
                Inquiry.objects.create(user=app_user, service=service_obj, subject=subject, message=message,
                                       image_1=image_1,
                                       image_2=image_2)
                return Response({'message': 'Inquiry submitted successfully', 'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            app_user = AppUser.objects.get(user=user)
            app_user.device_token = ''
            app_user.save()
            request.user.auth_token.delete()
            return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class UpdateOrderStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateOrderStatusSerializer
    model = Booking

    def post(self, request, *args, **kwargs):
        order_id = self.request.POST['id']
        status = self.request.POST['status']
        try:
            order_obj = Booking.objects.get(id=order_id)
            order_obj.status = status
            order_obj.save()
            AdminNotifications.objects.create(
                user=User.objects.get(email='admin@email.com'),
                title='Booking Update',
                body='Status of service request with id {} has been updated to {}'.format(order_obj.id,
                                                                                          order_obj.status)
            )
            return Response({'message': 'Order updated successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class ApplyPromoCodeView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def post(self, request, *args, **kwargs):
        order_id = self.request.POST['id']
        promocode = self.request.POST['promocode']
        try:
            order_obj = Booking.objects.get(id=order_id)
            order_obj.promocode = promocode
            order_obj.promocode_applied = True
            order_obj.save()
            return Response({'message': 'Promocode applied successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class UpcomingBooking(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        try:
            order_obj = Booking.objects.filter(Q(user=app_user, status='Started') | Q(user=app_user, status='started'))
            orders = []
            for obj in order_obj:
                orders.append(
                    {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                     'image_2': obj.service.image_2.url, 'price': obj.total, 'base_price': obj.service.base_price,
                     'date': obj.date, 'time': obj.time,
                     'address': obj.address, 'booking_status': obj.status})
            return Response({'data': orders, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class PastBooking(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        try:
            order_obj = Booking.objects.filter(user=app_user, status='Completed')
            orders = []
            # try:
            #     for obj in order_obj:
            #         print(obj)
            # except Exception as e:
            #     print(e)
            for obj in order_obj:
                try:
                    rating = RatingReview.objects.get(order=obj.id)
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'base_price': obj.service.base_price, 'price': obj.total,
                         'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating': rating.rating,
                         'review': rating.reviews, 'rating_status': True})
                except Exception as e:
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'base_price': obj.service.base_price, 'price': obj.total,
                         'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating_status': False})
            return Response({'data': orders, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class OnGoingBooking(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        try:
            order_obj = Booking.objects.filter(user=app_user, status='Accepted')
            orders = []
            for obj in order_obj:
                orders.append(
                    {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                     'image_2': obj.service.image_2.url, 'price': obj.total, 'base_price': obj.service.base_price,
                     'date': obj.date, 'time': obj.time,
                     'address': obj.address, 'booking_status': obj.status})
            return Response({'data': orders, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


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
                        {'user_name': obj.user.full_name, 'user_image': obj.user.profile_pic.url,
                         'rating': obj.rating,
                         'review': obj.reviews, 'created_at': obj.created_at})
                else:
                    ratings.append(
                        {'user_name': obj.user.full_name, 'user_image': '', 'rating': obj.rating,
                         'review': obj.reviews, 'created_at': obj.created_at})
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


class GetUserDetail(APIView):
    model = AppUser
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        return Response(
            {'country_code': app_user.user.country_code, 'phone_number': app_user.user.phone_number,
             'name': app_user.full_name})


class NotificationList(APIView):
    model = UserNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        notifications = UserNotification.objects.filter(user=app_user, read=False)
        notification_list = []
        for notification in notifications:
            notification_list.append(
                {'id': notification.id, 'title': notification.title, 'body': notification.body,
                 'created_at': notification.created_at})
        return Response({'data': notification_list, 'status': HTTP_200_OK})


class GetUserNotificationCount(APIView):
    model = UserNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        notification_count = UserNotification.objects.filter(user=app_user, read=False).count()
        return Response({'count': notification_count, 'status': HTTP_200_OK})


class UpdateNotification(APIView):
    model = UserNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        notifications = UserNotification.objects.filter(user=app_user, read=False)
        for notification in notifications:
            notification.read = True
            notification.save()
        return Response({'message': 'Notifications updates successfully', 'status': HTTP_200_OK})


class GetUsersBooking(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(user=user)
        bookings = Booking.objects.filter(user=app_user)
        return Response({'data': [{"id": booking.id} for booking in bookings], 'status': HTTP_200_OK})


class GetServiceName(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        services = Services.objects.all()
        return Response({'data': services.values(), 'status': HTTP_200_OK})


class ServiceProviderLogin(APIView):
    model = ServiceProvider
    serializer_class = ServiceProviderLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = ServiceProviderLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            device_token = serializer.validated_data['device_token']
            device_type = serializer.validated_data['device_type']
            try:
                user_obj = User.objects.get(email=email)
                check_password = user_obj.check_password(password)
                if check_password:
                    try:
                        existing_token = Token.objects.get(user=user_obj)
                        existing_token.delete()
                        token = Token.objects.get_or_create(user=user_obj)
                        service_provider = ServiceProvider.objects.get(email=email)
                        service_provider.device_token = device_token
                        service_provider.device_type = device_type
                        service_provider.save()
                        return Response(
                            {'message': "Logged in successfully", "token": token[0].key, "id": service_provider.id,
                             "full_name": service_provider.full_name,
                             'status': HTTP_200_OK})
                    except Exception as e:
                        token = Token.objects.get_or_create(user=user_obj)
                        service_provider = ServiceProvider.objects.get(email=email)
                        service_provider.device_token = device_token
                        service_provider.device_type = device_type
                        service_provider.save()
                        return Response(
                            {'message': "Logged in successfully", "token": token[0].key, "id": service_provider.id,
                             "full_name": service_provider.full_name,
                             'status': HTTP_200_OK})
                else:
                    return Response({'message': 'Incorrect password', 'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class ForgetPassword(APIView):
    model = User
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgetPasswordSerializer(data=self.request.data)
        if serializer.is_valid():
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']
            try:
                user = User.objects.get(country_code=country_code, phone_number=phone_number)
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password updated successfully", "status": HTTP_200_OK})
                else:
                    return Response(
                        {"message": "Password and Confirm password did not match", "status": HTTP_400_BAD_REQUEST})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class ServiceProviderLogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            app_user = ServiceProvider.objects.get(email=user.email)
            app_user.device_token = ''
            app_user.save()
            request.user.auth_token.delete()
            return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class ServiceProviderDashboard(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        service_provider_obj = ServiceProvider.objects.get(email=user.email)
        booking_obj = Booking.objects.filter(service_provider=service_provider_obj)
        active_booking_obj = Booking.objects.filter(service_provider=service_provider_obj, status='Started').count()
        completed_booking_obj = Booking.objects.filter(service_provider=service_provider_obj,
                                                       status='Completed').count()
        earning = 0
        for booking in booking_obj:
            print('ID--->>', booking.id)
            print('Total--->>', booking.total)
            try:
                earning += booking.total
            except Exception as e:
                earning += 0
        return Response(
            {'total_bookings': booking_obj.count(), 'active_booking': active_booking_obj,
             'completed_booking': completed_booking_obj, 'total_earning': earning})


class NewRequestView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        new_booking_list = []
        user = self.request.user
        service_provider_obj = ServiceProvider.objects.get(email=user.email)
        bookings_obj = Booking.objects.filter(service_provider=service_provider_obj, status='Started')
        return Response({'data': bookings_obj.values(), 'status': HTTP_200_OK})


class NewBookingRequestDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking
    serializer_class = NewBookingRequestDetailSerializer

    def post(self, request, *args, **kwargs):
        serializer = NewBookingRequestDetailSerializer(data=self.request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            try:
                booking_obj = Booking.objects.get(id=id)
                return Response({'id': booking_obj.id, 'date': booking_obj.date, 'status': booking_obj.status,
                                 'total': booking_obj.total, 'service_id': booking_obj.service.id,
                                 'service_name': booking_obj.service.service_name,
                                 'customer_name': booking_obj.user.full_name,
                                 'customer_contact_number': booking_obj.user.user.country_code + booking_obj.user.user.phone_number,
                                 'customer_address': booking_obj.address})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class UpdateBookingByServiceProvider(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking
    serializer_class = UpdateBookingByServiceProviderSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        service_provider = ServiceProvider.objects.get(email=user.email)
        serializer = UpdateBookingByServiceProviderSerializer(data=self.request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            status = serializer.validated_data['status']
            image_1 = serializer.validated_data['image_1']
            image_2 = serializer.validated_data['image_2']
            try:
                booking_obj = Booking.objects.get(id=id, service_provider=service_provider)
                booking_obj.status = status
                booking_obj.image_1 = image_1
                booking_obj.image_2 = image_2
                booking_obj.save()
                return Response({'message': 'Booking updated successfully', 'status': HTTP_200_OK})
            except Exception as e:
                return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class ServiceProviderCompletedTasks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        service_provider = ServiceProvider.objects.get(email=user.email)
        try:
            order_obj = Booking.objects.filter(service_provider=service_provider, status='Completed')
            orders = []
            for obj in order_obj:
                try:
                    rating = RatingReview.objects.get(order=obj.id)
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating': rating.rating,
                         'review': rating.reviews, 'rating_status': True})
                except Exception as e:
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating_status': False})
            return Response({'data': orders, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class ServiceProviderOnGoingTasks(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def get(self, request, *args, **kwargs):
        user = self.request.user
        service_provider = ServiceProvider.objects.get(email=user.email)
        try:
            order_obj = Booking.objects.filter(service_provider=service_provider, status='Accepted')
            orders = []
            for obj in order_obj:
                try:
                    rating = RatingReview.objects.get(order=obj.id)
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating': rating.rating,
                         'review': rating.reviews, 'rating_status': True})
                except Exception as e:
                    orders.append(
                        {'id': obj.id, 'service_name': obj.service.service_name, 'image_1': obj.service.image_1.url,
                         'image_2': obj.service.image_2.url, 'price': obj.total, 'date': obj.date, 'time': obj.time,
                         'address': obj.address, 'booking_status': obj.status, 'rating_status': False})
            return Response({'data': orders, 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class ProviderRegisterView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ProviderRegistration
    serializer_class = ProviderRegistrationSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            app_user = AppUser.objects.get(user=user)
            serializer = ProviderRegistrationSerializer(data=self.request.data)
            if serializer.is_valid():
                image = serializer.validated_data['image']
                service_provider_name = serializer.validated_data['service_provider_name']
                country_code = serializer.validated_data['country_code']
                phone_number = serializer.validated_data['phone_number']
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                ProviderRegistration.objects.create(user=app_user, image=image,
                                                    service_provider_name=service_provider_name,
                                                    country_code=country_code, phone_number=phone_number, email=email,
                                                    password=password)
                return Response(
                    {'message': "Provider registration request submitted successfully", 'status': HTTP_200_OK})
            else:
                return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class CouponList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = OffersAndDiscount

    def get(self, request, *args, **kwargs):
        coupons = OffersAndDiscount.objects.all()
        coupon_list = []
        for coupon in coupons:
            coupon_list.append({'id': coupon.id, 'coupon_code': coupon.coupon_code, 'percent': coupon.percent})
        return Response({'data': coupon_list, 'status': HTTP_200_OK})


class ApplyCoupon(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def post(self, request, *args, **kwargs):
        coupon = self.request.POST['coupon']
        order = self.request.POST['order']
        try:
            coupon_obj = OffersAndDiscount.objects.get(id=coupon)
            order_obj = Booking.objects.get(id=order)
            quote = order_obj.quote
            percent = coupon_obj.percent
            print(type((int(percent) / 100)))
            order_obj.sub_total = quote - (float((int(percent) / 100)) * quote)
            print(quote - float((int(percent) / 100)) * quote)
            order_obj.discount = (float((int(percent) / 100))) * quote
            order_obj.total = quote - (float((int(percent) / 100)) * quote) + order_obj.fees
            order_obj.promocode = coupon_obj.coupon_code
            order_obj.promocode_applied = True
            order_obj.save()
            return Response({'message': "Coupon applied successfully", 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class RemoveCoupoun(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Booking

    def post(self, request, *args, **kwargs):
        order = self.request.POST['order']
        try:
            order_obj = Booking.objects.get(id=order)
            order_obj.discount = 0
            order_obj.total = 0
            order_obj.sub_total = order_obj.quote
            order_obj.promocode = ''
            order_obj.promocode_applied = False
            order_obj.save()
            return Response({'message': 'Coupon removed successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class GuestUserToken(APIView):

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_superuser=True)
        # print(users)
        # print(users[0])
        token = Token.objects.get_or_create(user=users[0])
        return Response({'token': token[0].key, 'status': HTTP_200_OK})
