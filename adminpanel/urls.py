from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import LoginView, Dashboard, UserManagementView, ServiceProviderManagementView, SubAdminManagement, \
    CategoryView, OrderManagementView, VerificationManagementView, WorkerManagementView, OfferManagementView, \
    FinanceManagementView, StaticContentManagementView, NotificationManagementView, AdminProfileView, \
    ChangePasswordView, UserDetailView, ServiceProviderDetailView, SubAdminDetail, EditSubAdmin, AddServiceProvider, \
    CategoryDetail, AddCategoryView, SubCategoryView, SubCategoryDetail, AddSubCategory, AddSubAdmin, \
    AddServices, ServicesList, UpdateService, TopServicesView, TopServicesList, DeleteTopService, AssignServiceProvider, \
    SendQuoteView, RejectedOrderView, OfferDetailView, DeleteOfferView, UpdateOfferView, AddOffers, NotificationCount, \
    ReadNotificationView, InquiryView, UserProviderRegistrations, OrderDetail, UpdateContactUs, UpdateAboutUs, \
    UpdateTermsAndCondition, UpdatePrivacyPolicy, UnBlockUser, BlockUser, BlockServiceProvider, UnBlockServiceProvider, \
    DeleteSubAdmin, UpdateCategoryView, UpdateSubCategory, GetCategoryServiceProvider, CompletedOrders, \
    StaticPrivacyPolicyForAppStores, TermsAndConditionForAppStores, GetGstView, UpdateGstView, \
    ServiceProviderPasswordView, UserCsvView, OrderCsvView, ServiceProviderCsvView, CancelOrderView, HideCategory, \
    UnHideCategory

app_name = 'adminpanel'

urlpatterns = [
                  path('login/', LoginView.as_view(), name='login'),
                  path('dashboard/', Dashboard.as_view(), name='dashboard'),
                  path('user-management/', UserManagementView.as_view(), name='user-management'),
                  path('service-provider-management/', ServiceProviderManagementView.as_view(),
                       name='service-provider-management'),
                  path('sub-admin-management/', SubAdminManagement.as_view(), name='sub-admin-management'),
                  path('add-category/', AddCategoryView.as_view(), name='add-category'),
                  path('category-management/', CategoryView.as_view(), name='category-management'),
                  path('category-detail/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
                  path('hide-category/<int:pk>/', HideCategory.as_view(), name='hide-category'),
                  path('unhide-category/<int:pk>/', UnHideCategory.as_view(), name='unhide-category'),
                  path('update-category/<int:pk>/', UpdateCategoryView.as_view(), name='update-category'),
                  path('order-management/', OrderManagementView.as_view(), name='order-management'),
                  path('complete-orders/', CompletedOrders.as_view(), name='complete-orders'),
                  path('order-detail/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
                  path('rejected-order-management/', RejectedOrderView.as_view(), name='rejected-order-management'),
                  path('verification-management/', VerificationManagementView.as_view(),
                       name='verification-management'),
                  path('worker-management/', WorkerManagementView.as_view(), name='worker-management'),
                  path('add-offer/', AddOffers.as_view(), name='add-offer'),
                  path('offer-management/', OfferManagementView.as_view(), name='offer-management'),
                  path('offer-detail/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
                  path('offer-delete/<int:pk>/', DeleteOfferView.as_view(), name='offer-delete'),
                  path('update-offer/<int:pk>/', UpdateOfferView.as_view(), name='update-offer'),
                  path('finance-management/', FinanceManagementView.as_view(), name='finance-management'),
                  path('static-management/', StaticContentManagementView.as_view(), name='static-management'),
                  path('notification-management/', NotificationManagementView.as_view(),
                       name='notification-management'),
                  path('admin-profile/', AdminProfileView.as_view(), name='admin-profile'),
                  path('change-password/', ChangePasswordView.as_view(), name='change-password'),
                  path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
                  path('service-provider-detail/<int:pk>/', ServiceProviderDetailView.as_view(),
                       name='service-provider-detail'),
                  path('sub-admin-detail/<int:pk>/', SubAdminDetail.as_view(), name='sub-admin-detail'),
                  path('edit-sub-admin-detail/<int:pk>/', EditSubAdmin.as_view(), name='edit-sub-admin-detail'),
                  path('add-service-provider/', AddServiceProvider.as_view(), name='add-service-provider'),
                  path('add-sub-category/', AddSubCategory.as_view(), name='add-sub-category'),
                  path('sub-category-management/', SubCategoryView.as_view(), name='sub-category-management'),
                  path('service-provider-category/', GetCategoryServiceProvider.as_view(),
                       name='service-provider-category'),
                  path('sub-category-detail/<int:pk>/', SubCategoryDetail.as_view(), name='sub-category-detail'),
                  path('update-sub-category/<int:pk>/', UpdateSubCategory.as_view(), name='update-sub-category'),
                  path('add-sub-admin/', AddSubAdmin.as_view(), name='add-sub-admin'),
                  path('add-services/', AddServices.as_view(), name='add-services'),
                  path('services-list/', ServicesList.as_view(), name='services-list'),
                  path('update-service/<int:pk>/', UpdateService.as_view(), name='update-service'),
                  path('top-services/', TopServicesView.as_view(), name='top-services'),
                  path('top-services-list/', TopServicesList.as_view(), name='top-services-list'),
                  path('delete-top-service/<int:pk>/', DeleteTopService.as_view(), name='delete-top-service'),
                  path('assign-service-provider/', AssignServiceProvider.as_view(), name='assign-service-provider'),
                  path('send-quote/', SendQuoteView.as_view(), name='send-quote'),
                  path('cancel-order/', CancelOrderView.as_view(), name='cancel-order'),
                  path('notification-count/', NotificationCount.as_view(), name='notification-count'),
                  path('read-notification/', ReadNotificationView.as_view(), name='read-notification'),
                  path('inquiry/', InquiryView.as_view(), name='inquiry'),
                  path('privacy-policy-for-app-stores/', StaticPrivacyPolicyForAppStores.as_view(),
                       name='privacy-policy-for-app-stores'),
                  path('terms-and-condition-for-app-stores/', TermsAndConditionForAppStores.as_view(),
                       name='terms-and-condition-for-app-stores'),
                  path('update-contact-us/<int:pk>/', UpdateContactUs.as_view(), name='update-contact-us'),
                  path('update-about-us/<int:pk>/', UpdateAboutUs.as_view(), name='update-about-us'),
                  path('update-privacy-policy/<int:pk>/', UpdatePrivacyPolicy.as_view(), name='update-privacy-policy'),
                  path('unblock-user/<int:pk>/', UnBlockUser.as_view(), name='unblock-user'),
                  path('block-user/<int:pk>/', BlockUser.as_view(), name='block-user'),
                  path('block-service-provider/<int:pk>/', BlockServiceProvider.as_view(),
                       name='block-service-provider'),
                  path('unblock-service-provider/<int:pk>/', UnBlockServiceProvider.as_view(),
                       name='unblock-service-provider'),
                  path('delete-sub-admin/<int:pk>/', DeleteSubAdmin.as_view(), name='delete-sub-admin'),
                  path('update-gst/<int:pk>/', UpdateGstView.as_view(), name='update-gst'),
                  path('update-terms-and-condition/<int:pk>/', UpdateTermsAndCondition.as_view(),
                       name='update-terms-and-condition'),
                  path('user-provider-registration/', UserProviderRegistrations.as_view(),
                       name='user-provider-registration'),
                  path('get-gst/', GetGstView.as_view(), name='get-gst'),
                  path('service-provider-password/<int:pk>/', ServiceProviderPasswordView.as_view(),
                       name='service-provider-password'),
                  path('user-csv/', UserCsvView.as_view(), name='user-csv'),
                  path('bookings-csv/', OrderCsvView.as_view(), name='bookings-csv'),
                  path('service-provider-csv/', ServiceProviderCsvView.as_view(), name='service-provider-csv'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
