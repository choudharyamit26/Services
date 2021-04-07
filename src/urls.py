from .views import CreateUser, LoginView, CheckUserExists, UpdateUserProfile, GetUserProfilePic, UpdateUserLanguage, \
    HomeView, SearchingServices, SaveSearchesHistory, GetUserPastSearches, BookingView, GetBookingDetail, ContactUsView, \
    PrivacyPolicyView, TermsAndConditionView, AboutUsView, GeneralInquiryView, LogoutView, UpcomingBooking, PastBooking, \
    OnGoingBooking, UpdateOrderStatus, RatingAndReviews, GetServiceReviewRatings, GetDefaultOfferPercentView, \
    GetAllOffersAndDiscount, GetUserDetail, NotificationList, GetUserNotificationCount, UpdateNotification, \
    GetSubCategory, GetServices, GetServiceDetail, GetUsersBooking, InquiryView, GetServiceName, ServiceProviderLogin, \
    ForgetPassword, ServiceProviderLogoutView, ServiceProviderDashboard, NewRequestView, NewBookingRequestDetail, \
    UpdateBookingByServiceProvider, ServiceProviderCompletedTasks, ServiceProviderOnGoingTasks,ProviderRegisterView
from django.urls import path

app_name = 'src'

urlpatterns = [
    path('user-create/', CreateUser.as_view(), name='user-create'),
    path('user-login/', LoginView.as_view(), name='user-login'),
    path('check-user-exists/', CheckUserExists.as_view(), name='check-user-exists'),
    path('update-user-profile-pic/', UpdateUserProfile.as_view(), name='update-user-profile-pic'),
    path('get-user-profile-pic/', GetUserProfilePic.as_view(), name='get-user-profile-pic'),
    path('update-user-language/', UpdateUserLanguage.as_view(), name='update-user-language'),
    path('home-api/', HomeView.as_view(), name='home-api'),
    path('search-services/', SearchingServices.as_view(), name='search-services'),
    path('save-search/', SaveSearchesHistory.as_view(), name='save-search'),
    path('get-saved-searches/', GetUserPastSearches.as_view(), name='get-saved-searches'),
    path('book-service/', BookingView.as_view(), name='book-service'),
    path('upcoming-bookings/', UpcomingBooking.as_view(), name='upcoming-bookings'),
    path('past-bookings/', PastBooking.as_view(), name='past-bookings'),
    path('ongoing-bookings/', OnGoingBooking.as_view(), name='ongoing-bookings'),
    path('booking-detail/', GetBookingDetail.as_view(), name='booking-detail'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-and-condition/', TermsAndConditionView.as_view(), name='terms-and-condition'),
    path('about-us/', AboutUsView.as_view(), name='about-us'),
    path('help-with-order/', GeneralInquiryView.as_view(), name='help-with-order'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('update-order/', UpdateOrderStatus.as_view(), name='update-order'),
    path('ratings-and-review/', RatingAndReviews.as_view(), name='ratings-and-review'),
    path('service-ratings-and-review/', GetServiceReviewRatings.as_view(), name='service-ratings-and-review'),
    path('get-default-discount-percent/', GetDefaultOfferPercentView.as_view(), name='get-default-discount-percent'),
    path('get-all-offers/', GetAllOffersAndDiscount.as_view(), name='get-all-offers'),
    path('get-user-detail/', GetUserDetail.as_view(), name='get-user-detail'),
    path('get-user-notification-list/', NotificationList.as_view(), name='get-user-notification-list'),
    path('get-user-notification-count/', GetUserNotificationCount.as_view(), name='get-user-notification-count'),
    path('update-user-notification/', UpdateNotification.as_view(), name='update-user-notification'),
    path('get-subcategories/', GetSubCategory.as_view(), name='get-subcategories'),
    path('get-services/', GetServices.as_view(), name='get-services'),
    path('get-service-detail/', GetServiceDetail.as_view(), name='get-service-detail'),
    path('get-users-bookings-ids/', GetUsersBooking.as_view(), name='get-users-bookings-ids'),
    path('general-inquiry/', InquiryView.as_view(), name='general-inquiry'),
    path('services/', GetServiceName.as_view(), name='services'),
    path('service-provider-login/', ServiceProviderLogin.as_view(), name='service-provider-login'),
    path('forget-password/', ForgetPassword.as_view(), name='forget-password'),
    path('service-provider-logout/', ServiceProviderLogoutView.as_view(), name='service-provider-logout'),
    path('service-provider-dashboard/', ServiceProviderDashboard.as_view(), name='service-provider-dashboard'),
    path('new-booking-requests/', NewRequestView.as_view(), name='new-booking-requests'),
    path('new-booking-request-detail/', NewBookingRequestDetail.as_view(), name='new-booking-request-detail'),
    path('update-booking-status-by-service-provider/', UpdateBookingByServiceProvider.as_view(),
         name='update-booking-status-by-service-provider'),
    path('service-provider-completed-tasks/', ServiceProviderCompletedTasks.as_view(),
         name='service-provider-completed-tasks'),
    path('service-provider-on-going-tasks/', ServiceProviderOnGoingTasks.as_view(),
         name='service-on-going-completed-tasks'),
    path('provider-register-from-user-app/',ProviderRegisterView.as_view(),name='provider-register-from-user-app')
]
