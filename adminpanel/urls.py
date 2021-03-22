from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import LoginView, Dashboard, UserManagementView, ServiceProviderManagementView, SubAdminManagement, \
    CategoryView, OrderManagementView, VerificationManagementView, WorkerManagementView, OfferManagementView, \
    FinanceManagementView, StaticContentManagementView, NotificationManagementView, AdminProfileView, \
    ChangePasswordView, UserDetailView, ServiceProviderDetailView, SubAdminDetail, EditSubAdmin, AddServiceProvider, \
    CategoryDetail, AddCategoryView, SubCategoryView, SubCategoryDetail, AddSubCategory, AddSubAdmin, BlockUser, \
    AddServices, ServicesList, UpdateService, TopServicesView, TopServicesList, DeleteTopService, AssignServiceProvider, \
    SendQuoteView,RejectedOrderView

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
                  path('order-management/', OrderManagementView.as_view(), name='order-management'),
                  path('rejected-order-management/', RejectedOrderView.as_view(), name='rejected-order-management'),
                  path('verification-management/', VerificationManagementView.as_view(),
                       name='verification-management'),
                  path('worker-management/', WorkerManagementView.as_view(), name='worker-management'),
                  path('offer-management/', OfferManagementView.as_view(), name='offer-management'),
                  path('finance-management/', FinanceManagementView.as_view(), name='finance-management'),
                  path('static-management/', StaticContentManagementView.as_view(), name='static-management'),
                  path('notification-management/', NotificationManagementView.as_view(),
                       name='notification-management'),
                  path('admin-profile/', AdminProfileView.as_view(), name='admin-profile'),
                  path('change-password/', ChangePasswordView.as_view(), name='change-password'),
                  path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
                  path('service-provider-detail/<int:pk>/', ServiceProviderDetailView.as_view(),
                       name='service-provider-detail'),
                  path('sub-admin-detail/', SubAdminDetail.as_view(), name='sub-admin-detail'),
                  path('edit-sub-admin-detail/', EditSubAdmin.as_view(), name='edit-sub-admin-detail'),
                  path('add-service-provider/', AddServiceProvider.as_view(), name='add-service-provider'),
                  path('add-sub-category/', AddSubCategory.as_view(), name='add-sub-category'),
                  path('sub-category-management/', SubCategoryView.as_view(), name='sub-category-management'),
                  path('sub-category-detail/<int:pk>/', SubCategoryDetail.as_view(), name='sub-category-detail'),
                  path('add-sub-admin/', AddSubAdmin.as_view(), name='add-sub-admin'),
                  path('add-services/', AddServices.as_view(), name='add-services'),
                  path('services-list/', ServicesList.as_view(), name='services-list'),
                  path('update-service/<int:pk>/', UpdateService.as_view(), name='update-service'),
                  path('block-user/<int:pk>/', BlockUser.as_view(), name='block-user'),
                  path('top-services/', TopServicesView.as_view(), name='top-services'),
                  path('top-services-list/', TopServicesList.as_view(), name='top-services-list'),
                  path('delete-top-service/<int:pk>/', DeleteTopService.as_view(), name='delete-top-service'),
                  path('assign-service-provider/', AssignServiceProvider.as_view(), name='assign-service-provider'),
                  path('send-quote/', SendQuoteView.as_view(), name='send-quote'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
