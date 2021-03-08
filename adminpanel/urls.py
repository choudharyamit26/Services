from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import LoginView, Dashboard, UserManagementView, ServiceProviderManagementView, SubAdminManagementView, \
    CategoryView, OrderManagementView, VerificationManagementView, WorkerManagementView, OfferManagementView, \
    FinanceManagementView, StaticContentManagementView, NotificationManagementView, AdminProfileView, \
    ChangePasswordView, UserDetailView, ServiceProviderDetailView, SubAdminDetail, EditSubAdmin, AddServiceProvider, \
    CategoryDetail, AddCategoryView

app_name = 'adminpanel'

urlpatterns = [
                  path('login/', LoginView.as_view(), name='login'),
                  path('dashboard/', Dashboard.as_view(), name='dashboard'),
                  path('user-management/', UserManagementView.as_view(), name='user-management'),
                  path('service-provider-management/', ServiceProviderManagementView.as_view(),
                       name='service-provider-management'),
                  path('sub-admin-management/', SubAdminManagementView.as_view(), name='sub-admin-management'),
                  path('add-category/', AddCategoryView.as_view(), name='add-category'),
                  path('category-management/', CategoryView.as_view(), name='category-management'),
                  path('category-detail/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
                  path('order-management/', OrderManagementView.as_view(), name='order-management'),
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
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
