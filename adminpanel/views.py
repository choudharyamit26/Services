import csv
from datetime import date
from django.db.models import Sum
from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, DetailView, UpdateView, FormView, TemplateView, ListView, CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from .filters import OrderFilter, OrderFilter2
from .forms import AddServiceProviderForm, AddCategoryForm, SubCategoryForm, SubAdminForm, UpdateServiceForm, \
    AssignServiceProviderForm, UpdateOfferForm, ContactUsForm, AboutUsForm, TermsAndConditionForm, PrivacyPolicyForm
from .models import User, Category, ServiceProvider, SubCategory, Services, TopServices, AdminNotifications
from src.models import Booking, OffersAndDiscount, AppUser, GeneralInquiry, Inquiry, ProviderRegistration, ContactUs, \
    PrivacyPolicy, TermsAndCondition, AboutUs, UserNotification, Settings, Gst
from src.fcm_notification import send_to_one, send_another


class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'login.html')

    def post(self, request, *args, **kwargs):
        email = self.request.POST['email']
        password = self.request.POST['password']
        try:
            user_object = User.objects.get(email=email)
            if user_object.check_password(password):
                if user_object.is_superuser or user_object.is_sub_admin:
                    login(self.request, user_object)
                    messages.success(self.request, "Logged in successfully")
                    return redirect("adminpanel:dashboard")
                else:
                    messages.error(self.request, "You are not authorised please contact admin")
                    return redirect("adminpanel:login")
            else:
                messages.error(self.request, 'Incorrect Password')
                return redirect("adminpanel:login")
        except Exception as e:
            print(e)
            messages.error(self.request, "User does not exists")
            return redirect("adminpanel:login")


class Dashboard(LoginRequiredMixin, View):
    template_name = 'dashboard.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'dashboard.html')


class UserManagementView(LoginRequiredMixin, View):
    template_name = 'user-management.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        users = AppUser.objects.all().exclude(user__email='roo3a8025@gmail.com').order_by('-id')
        return render(self.request, 'user-management.html', {'object_list': users})


class UserCsvView(LoginRequiredMixin, View):
    model = AppUser
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(
            ['User Id', 'Name', 'Phone Number', 'Registration Date'])
        users = AppUser.objects.all().values_list('id', 'full_name', 'user__phone_number', 'created_at')
        for user in users:
            writer.writerow(user)
        return response


class OrderCsvView(LoginRequiredMixin, View):
    model = Booking
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        writer = csv.writer(response)
        writer.writerow(
            ['Booking Id', 'User Name', 'User Phone Number', 'Ordered At', 'Ordered For', 'Ordered Time',
             'Ordered Amount'])
        bookings = Booking.objects.all().exclude(status='Completed').exclude(status='Rejected').values_list('id',
                                                                                                            'user__full_name',
                                                                                                            'user__user__phone_number',
                                                                                                            'created_at__date',
                                                                                                            'date',
                                                                                                            'time',
                                                                                                            'total')
        for booking in bookings:
            writer.writerow(booking)
        return response


class ServiceProviderCsvView(LoginRequiredMixin, View):
    model = ServiceProvider
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service-provider.csv"'
        writer = csv.writer(response)
        writer.writerow(
            ['Id', 'User Name', 'User Email', 'Category', 'Sub Category', 'Services',
             'Address'])
        serviceproviders = ServiceProvider.objects.all().values_list('id',
                                                                     'full_name',
                                                                     'email',
                                                                     'category__category_name',
                                                                     'sub_category__sub_category_name',
                                                                     'services__service_name', 'address')
        for serviceprovider in serviceproviders:
            writer.writerow(serviceprovider)
        return response


class UnBlockUser(LoginRequiredMixin, View):
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        print(args)
        user = AppUser.objects.get(id=kwargs['pk'])
        user.is_blocked = False
        user.save()
        messages.success(self.request, "User Unblocked successfully")
        return redirect("adminpanel:user-management")


class BlockUser(LoginRequiredMixin, View):
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        user = AppUser.objects.get(id=kwargs['pk'])
        user.is_blocked = True
        user.save()
        messages.success(self.request, "User blocked successfully")
        return redirect("adminpanel:user-management")


class ServiceProviderManagementView(LoginRequiredMixin, View):
    template_name = 'service-provider-management.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'service-provider-management.html', {'object_list': ServiceProvider.objects.all()})


class ServiceProviderPasswordView(LoginRequiredMixin, View):
    template_name = 'password-management.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(kwargs)
        service_provider = ServiceProvider.objects.get(id=kwargs['pk'])
        return render(self.request, 'password-management.html',
                      {'provider_name': service_provider.full_name})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        print(kwargs)
        service_provider = ServiceProvider.objects.get(id=kwargs['pk'])
        user = User.objects.get(email=service_provider.email)
        if self.request.POST.get('new_password1') == self.request.POST.get('new_password2'):
            user.set_password(self.request.POST.get('new_password1'))
            user.save()
            messages.success(self.request, 'Password changed successfully')
            return redirect("adminpanel:service-provider-management")
        else:
            messages.error(self.request, 'New Password and Confirm Password did not match')
            return redirect(self.request.path_info)


class BlockServiceProvider(LoginRequiredMixin, View):
    model = ServiceProvider
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        service_provider = ServiceProvider.objects.get(id=kwargs['pk'])
        service_provider.is_blocked = True
        service_provider.save()
        user = User.objects.get(email=service_provider.email)
        user.is_blocked = True
        user.save()
        messages.success(self.request, "Service Provider Blocked Successfully")
        return redirect("adminpanel:service-provider-management")


class UnBlockServiceProvider(LoginRequiredMixin, View):
    model = ServiceProvider
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        service_provider = ServiceProvider.objects.get(id=kwargs['pk'])
        service_provider.is_blocked = False
        service_provider.save()
        user = User.objects.get(email=service_provider.email)
        user.is_blocked = False
        user.save()
        messages.success(self.request, "Service Provider Unblocked Successfully")
        return redirect("adminpanel:service-provider-management")


# class SubAdminManagementView(View):
#     template_name = 'sub-admin-management.html'
#
#     def get(self, request, *args, **kwargs):
#         return render(self.request, 'sub-admin-management.html')


class CategoryView(LoginRequiredMixin, ListView):
    template_name = 'Category.html'
    model = Category
    login_url = "adminpanel:login"

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'Category.html')


class HideCategory(LoginRequiredMixin, View):
    model = Category
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print('>>>>>>>>', kwargs)
        category_obj = Category.objects.get(id=kwargs['pk'])
        category_obj.hidden = True
        category_obj.save()
        messages.success(self.request, 'Category made hidden successfully')
        return redirect("adminpanel:category-management")


class UnHideCategory(LoginRequiredMixin, View):
    model = Category
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print('>>>>>>>>', kwargs)
        category_obj = Category.objects.get(id=kwargs['pk'])
        category_obj.hidden = False
        category_obj.save()
        messages.success(self.request, 'Category made unhidden successfully')
        return redirect("adminpanel:category-management")


class AddCategoryView(LoginRequiredMixin, CreateView):
    template_name = 'addCategory.html'
    model = Category
    form_class = AddCategoryForm
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        # image = self.request.POST.get('category_image' or None)
        image = self.request.FILES.get('category_image' or None)
        print(image)
        print(type(image))
        category_name = self.request.POST['category_name']
        category_name_arabic = self.request.POST['category_name_arabic']
        Category.objects.create(
            category_image=image,
            category_name=category_name.lower(),
            category_name_arabic=category_name_arabic
        )
        messages.success(self.request, 'Category added successfully')
        return redirect("adminpanel:category-management")


class CategoryDetail(LoginRequiredMixin, DetailView):
    template_name = 'categoryDetails.html'
    model = Category
    login_url = "adminpanel:login"


class UpdateCategoryView(LoginRequiredMixin, UpdateView):
    template_name = 'update-category.html'
    model = Category
    form_class = AddCategoryForm

    def get(self, request, *args, **kwargs):
        return render(self.request, 'update-category.html', {'object': Category.objects.get(id=kwargs['pk'])})

    def post(self, request, *args, **kwargs):
        category_obj = Category.objects.get(id=kwargs['pk'])
        category_obj.category_image = self.request.FILES.get('category_image' or None)
        category_obj.category_name = self.request.POST['category_name']
        category_obj.category_name_arabic = self.request.POST['category_name_arabic']
        category_obj.save()
        messages.success(self.request, "Category updated successfully")
        return redirect("adminpanel:category-management")


class OrderManagementView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'order-management.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('status'):
            bookings = Booking.objects.filter(status=self.request.GET.get('status')).order_by('-id')
            print(bookings)
            return render(self.request, 'order-management.html',
                          {'object_list': bookings,
                           'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})
        else:
            bookings = Booking.objects.all().exclude(status='Completed').exclude(status='Rejected').exclude(
                is_canceled_by_admin=True).order_by('-id')
            return render(self.request, 'order-management.html',
                          {'object_list': bookings,
                           'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})

    def post(self, request, *args, **kwargs):
        from_date = self.request.POST.get('from_date' or None)
        # print(from_date)
        # for i in Booking.objects.all():
        #     print(i.created_at)
        # print(self.request.POST)

        to_date = self.request.POST.get('to_date' or None)
        from_date_2 = self.request.POST.get('order_on_from_date' or None)
        order_on_from_date_2 = self.request.POST.get('order_on_to_date' or None)
        if from_date_2:
            if from_date_2 == order_on_from_date_2:
                bookings = Booking.objects.filter(created_at__date=from_date_2)
                return render(self.request, 'order-management.html',
                              {'object_list': bookings,
                               'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})
            else:
                bookings = Booking.objects.filter(created_at__range=(from_date_2, order_on_from_date_2)).order_by('-id')
                return render(self.request, 'order-management.html',
                              {'object_list': bookings,
                               'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})
        elif from_date:
            if from_date == to_date:
                date_split = from_date.split('-')
                year = int(date_split[0])
                month = int(date_split[1])
                day = int(date_split[2])
                bookings = Booking.objects.filter(date__contains=date(year, month, day))
                return render(self.request, 'order-management.html',
                              {'object_list': bookings,
                               'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})
            else:
                bookings = Booking.objects.filter(created_at__range=(from_date, to_date)).order_by('-id')
                return render(self.request, 'order-management.html',
                              {'object_list': bookings,
                               'service_provider': ServiceProvider.objects.all(), 'categories': Category.objects.all()})


class CancelOrderView(LoginRequiredMixin, View):
    model = Booking
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print('From cancel order-->>', self.request.POST)
        reason = self.request.POST['quote']
        order_obj = Booking.objects.get(id=self.request.POST['orderId'])
        order_obj.is_canceled_by_admin = True
        order_obj.cancellation_reason_by_admin = reason
        order_obj.save()
        user_device_type = order_obj.user.device_type
        user_device_token = order_obj.user.device_token
        if user_device_type == 'android':
            if Settings.objects.get(user=order_obj.user).language == 'en':
                UserNotification.objects.create(user=order_obj.user, title='ORDER CANCELED BY ADMIN',
                                                body=f'Your order with order ID {order_obj.id} has been rejected by admin. {reason}')
                data = {
                    "title": "ORDER CANCELED BY ADMIN",
                    "body": f"Your order with order ID {order_obj.id} has been rejected by admin. {reason}",
                    "type": "canceled_services"
                }
                respo = send_to_one(user_device_token, data)
                print(respo)
            else:
                UserNotification.objects.create(user=order_obj.user, title="تم إلغاء الطلب من قبل المسؤول",
                                                body=f'رفض المشرف طلبك الذي يحتوي على معرّف الطلب {order_obj.id}. {reason}')
                data = {
                    "title": "تم إلغاء الطلب من قبل المسؤول",
                    "body": f"رفض المشرف طلبك الذي يحتوي على معرّف الطلب {order_obj.id}. {reason}",
                    "type": "upcoming_services"
                }
                respo = send_to_one(user_device_token, data)
                print(respo)
        else:
            if Settings.objects.get(user=order_obj.user).language == 'en':
                UserNotification.objects.create(user=order_obj.user, title='ORDER CANCELED BY ADMIN',
                                                body=f'Your order with order ID {order_obj.id} has been rejected by admin. {reason}')
                title = "ORDER CANCELED BY ADMIN"
                body = f"Your order with order ID {order_obj.id} has been rejected by admin. {reason}"
                message_type = "newQuote"
                # sound = 'notifications.mp3'
                respo = send_another(user_device_token, title, body, message_type)
                print(respo)
            else:
                UserNotification.objects.create(user=order_obj.user, title="تم إلغاء الطلب من قبل المسؤول",
                                                body=f"رفض المشرف طلبك الذي يحتوي على معرّف الطلب {order_obj.id}. {reason}"),
                title = "تم إلغاء الطلب من قبل المسؤول"
                body = f"رفض المشرف طلبك الذي يحتوي على معرّف الطلب {order_obj.id}. {reason}",
                message_type = "newQuote"
                # sound = 'notifications.mp3'
                respo = send_another(user_device_token, title, body, message_type)
                print(respo)
        messages.success(self.request, 'Order canceled successfully')
        return redirect("adminpanel:order-management")


class CompletedOrders(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'complete-orders.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.filter(status='Completed').order_by('-id')
        order_filter = OrderFilter(self.request.GET, queryset=bookings)
        bookings = order_filter.qs
        return render(self.request, 'complete-orders.html',
                      {'object_list': bookings})


class GetCategoryServiceProvider(LoginRequiredMixin, View):
    model = ServiceProvider
    login_url = "adminpanel:login"
    template_name = 'category-provider.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'category-provider.html',
                      {'service_provider': ServiceProvider.objects.filter(category=self.request.GET['categoryId'])})


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'order-detail.html'
    login_url = "adminpanel:login"


class RejectedOrderView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'rejected-order-management.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'rejected-order-management.html',
                      {'object_list': Booking.objects.filter(status='Rejected')})


class AssignServiceProvider(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'order-management.html'
    form_class = AssignServiceProviderForm
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print('From Assign Service Provider', self.request.POST)
        order = self.request.POST['orderId']
        service_provider_id = self.request.POST['serviceProviderId']
        admin_percent = self.request.POST['admin_percent']
        order_obj = Booking.objects.get(id=order)
        order_obj.admin_percent = admin_percent
        # order_obj.fees = (float(admin_percent) / 100) * order_obj.quote
        order_obj.service_provider = ServiceProvider.objects.get(id=service_provider_id)
        order_obj.save()
        service_provider_device_type = order_obj.service_provider.device_type
        service_provider_device_token = order_obj.service_provider.device_token
        # if service_provider_device_type == 'android':
        #     data = {
        #         "title": "New Message",
        #         "body": f"You have received a new service request for order with order ID {order_obj.id}"
        #     }
        #     respo = send_to_one(service_provider_device_token, data)
        #     print(respo)
        # else:
        title = "New Order"
        body = f"You have received a new service request for order with order ID {order_obj.id}"
        message_type = "NewOrder"
        # sound = 'notifications.mp3'
        respo = send_another(service_provider_device_token, title, body, message_type)
        print(respo)
        messages.success(self.request, 'Service provider assigned successfully')
        return redirect("adminpanel:order-management")


class SendQuoteView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'order-management.html'
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print('>>>>>>>>>>>>>>>>>>>>>', self.request.POST)
        order_obj = Booking.objects.get(id=self.request.POST['orderId'])
        order_obj.quote = self.request.POST['quote']
        order_obj.sub_total = self.request.POST['quote']
        if order_obj.night_booking:
            order_obj.total = float(self.request.POST['quote']) + 100 + Gst.objects.all()[0].gst
        else:
            order_obj.total = float(self.request.POST['quote']) + Gst.objects.all()[0].gst
        order_obj.save()
        user_device_type = order_obj.user.device_type
        user_device_token = order_obj.user.device_token
        if user_device_type == 'android':
            if Settings.objects.get(user=order_obj.user).language == 'en':
                UserNotification.objects.create(user=order_obj.user, title='"OFFERED PRICE"',
                                                body=f'You have received a offered price for order with order ID {order_obj.id}')
                data = {
                    "title": "OFFERED PRICE",
                    "body": f"You have received a offered price for order with order ID {order_obj.id}",
                    "type": "upcoming_services"
                }
                respo = send_to_one(user_device_token, data)
                print(respo)
            else:
                UserNotification.objects.create(user=order_obj.user, title="السعر المعروض",
                                                body=f' لقد استلمتم عرض سعر للطلب  الرجاء مراجعته واعلامنا بردك !')
                data = {
                    "title": "السعر المعروض",
                    "body": f" لقد استلمتم عرض سعر للطلب  الرجاء مراجعته واعلامنا بردك !",
                    "type": "upcoming_services"
                }
                respo = send_to_one(user_device_token, data)
                print(respo)
        else:
            if Settings.objects.get(user=order_obj.user).language == 'en':
                UserNotification.objects.create(user=order_obj.user, title='OFFERED PRICE',
                                                body=f'You have received a offered price for order with order ID {order_obj.id}')
                title = "OFFERED PRICE"
                body = f"You have received a offered price for order with order ID {order_obj.id}"
                message_type = "newQuote"
                # sound = 'notifications.mp3'
                respo = send_another(user_device_token, title, body, message_type)
                print(respo)
            else:
                UserNotification.objects.create(user=order_obj.user, title="السعر المعروض",
                                                body=f" لقد استلمتم عرض سعر للطلب  الرجاء مراجعته واعلامنا بردك !"),
                title = "السعر المعروض"
                body = f" لقد استلمتم عرض سعر للطلب  الرجاء مراجعته واعلامنا بردك !",
                message_type = "newQuote"
                # sound = 'notifications.mp3'
                respo = send_another(user_device_token, title, body, message_type)
                print(respo)
        return redirect("adminpanel:order-management")


class VerificationManagementView(LoginRequiredMixin, View):
    template_name = 'verification.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'verification.html')


class WorkerManagementView(LoginRequiredMixin, View):
    template_name = 'worker.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'worker.html')


class OfferManagementView(LoginRequiredMixin, View):
    template_name = 'offer.html'
    model = OffersAndDiscount
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'offer.html', {'object_list': OffersAndDiscount.objects.all()})


class OfferDetailView(LoginRequiredMixin, DetailView):
    template_name = 'viewoffer.html'
    model = OffersAndDiscount
    login_url = "adminpanel:login"


class DeleteOfferView(LoginRequiredMixin, DeleteView):
    template_name = 'delete-offer.html'
    model = OffersAndDiscount
    success_url = reverse_lazy("adminpanel:offer-management")
    login_url = "adminpanel:login"


class UpdateOfferView(LoginRequiredMixin, UpdateView):
    template_name = 'update-coupon.html'
    model = OffersAndDiscount
    form_class = UpdateOfferForm
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        offer_obj = OffersAndDiscount.objects.get(id=kwargs['pk'])
        offer_obj.coupon_code = (self.request.POST['coupon_code']).upper()
        offer_obj.percent = self.request.POST['percent']
        offer_obj.save()
        messages.success(self.request, "Offer updated successfully")
        return redirect("adminpanel:offer-management")


class AddOffers(LoginRequiredMixin, CreateView):
    template_name = 'update-coupon.html'
    model = OffersAndDiscount
    form_class = UpdateOfferForm
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        coupon_code = self.request.POST['coupon_code']
        OffersAndDiscount.objects.create(coupon_code=coupon_code.upper(), percent=self.request.POST['percent'])
        messages.success(self.request, 'Offer added successfully')
        return redirect("adminpanel:offer-management")


class FinanceManagementView(LoginRequiredMixin, View):
    template_name = 'finance.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'finance.html')


class StaticContentManagementView(LoginRequiredMixin, ListView):
    template_name = 'static.html'
    model = ContactUs
    login_url = "adminpanel:login"

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'static.html')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_us'] = ContactUs.objects.all().first()
        context['terms_condition'] = TermsAndCondition.objects.all().first()
        context['privacy_policy'] = PrivacyPolicy.objects.all().first()
        context['about_us'] = AboutUs.objects.all().first()
        return context


class UpdateContactUs(LoginRequiredMixin, UpdateView):
    template_name = 'update-contact-us.html'
    model = ContactUs
    form_class = ContactUsForm
    success_url = reverse_lazy("adminpanel:static-management")
    login_url = "adminpanel:login"


class UpdateAboutUs(LoginRequiredMixin, UpdateView):
    template_name = 'update-about-us.html'
    model = AboutUs
    form_class = AboutUsForm
    success_url = reverse_lazy("adminpanel:static-management")
    login_url = "adminpanel:login"


class UpdateTermsAndCondition(LoginRequiredMixin, UpdateView):
    template_name = 'update-terms-condition.html'
    model = TermsAndCondition
    form_class = TermsAndConditionForm
    success_url = reverse_lazy("adminpanel:static-management")
    login_url = "adminpanel:login"


class UpdatePrivacyPolicy(LoginRequiredMixin, UpdateView):
    template_name = 'update-privacy-policy.html'
    model = PrivacyPolicy
    form_class = PrivacyPolicyForm
    success_url = reverse_lazy("adminpanel:static-management")
    login_url = "adminpanel:login"


class NotificationManagementView(LoginRequiredMixin, ListView):
    template_name = 'notification.html'
    model = AdminNotifications
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'notification.html',
                      {'object_list': AdminNotifications.objects.all().order_by('-id')})


class ReadNotificationView(LoginRequiredMixin, View):
    model = AdminNotifications
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        notifications = AdminNotifications.objects.filter(read=False)
        for notification in notifications:
            notification.read = True
            notification.save()
        return HttpResponse('Read all notification')


class AdminProfileView(LoginRequiredMixin, View):
    template_name = 'myprofile.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'myprofile.html')


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'changePassword.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'changePassword.html')


class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = 'userdetail.html'
    model = User
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, "userdetail.html", {'object': AppUser.objects.get(id=kwargs['pk']),
                                                        'bookings': Booking.objects.filter(user=kwargs['pk'])})

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = Booking.objects.filter(user=kwargs['object'].id)
        context['bookings'] = bookings
        return context


class ServiceProviderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'servicedetails.html'
    model = ServiceProvider
    login_url = "adminpanel:login"

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = Booking.objects.filter(service_provider=kwargs['object'].id)
        bookings_amount = Booking.objects.filter(service_provider=kwargs['object'].id).aggregate(Sum('total'))
        print(bookings_amount)
        context['bookings'] = bookings
        context['bookings_amount'] = bookings_amount['total__sum']
        return context


class SubAdminDetail(LoginRequiredMixin, DetailView):
    template_name = 'view-admin.html'
    model = User
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'view-admin.html', {'object': User.objects.get(id=kwargs['pk'])})


class DeleteSubAdmin(LoginRequiredMixin, View):
    model = User
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['pk'])
        user.delete()
        messages.success(self.request, "User deleted successfully")
        return redirect("adminpanel:sub-admin-management")


class EditSubAdmin(LoginRequiredMixin, View):
    template_name = 'edit-admin.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'edit-admin.html', {'object': User.objects.get(id=kwargs['pk'])})

    def post(self, request, *args, **kwargs):
        name = self.request.POST['full_name']
        email = self.request.POST['email']
        phone_number = self.request.POST['phone_number']
        # password = self.request.POST['password']
        # confirm_password = self.request.POST['confirm_password']
        access_rights = self.request.POST.getlist('access_rights')
        print(access_rights)
        # try:
        #     user_obj = User.objects.get(Q(email=email) | Q(phone_number=phone_number))
        #     messages.error(self.request, 'User with this email/phone already exists')
        #     return render(self.request, 'add-admin.html')
        # except Exception as e:
        # print('Exception----->>>', e)
        # user = User.objects.create(
        #     full_name=name,
        #     email=email,
        #     phone_number=phone_number,
        #     is_sub_admin=True
        # )
        user = User.objects.get(id=kwargs['pk'])
        user.full_name = name
        user.email = email
        user.phone_number = phone_number
        for right in access_rights:
            if '_'.join(right.lower().split()) == 'can_manage_user':
                user.can_manage_user = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_order':
                user.can_manage_order = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_provider':
                user.can_manage_provider = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_category':
                user.can_manage_category = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_sub_category':
                user.can_manage_sub_category = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_services':
                user.can_manage_services = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_subadmin':
                user.can_manage_subadmin = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_top_services':
                user.can_manage_top_services = True
                user.save()
            if '_'.join(right.lower().split()) == 'can_manage_coupons':
                user.can_manage_coupons = True
                user.save()
        messages.success(self.request, 'Sub Admin edited successfully')
        return redirect("adminpanel:sub-admin-management")


class PasswordResetConfirmView(LoginRequiredMixin, View):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = User.objects.get(id=uid)
        token_generator = default_token_generator
        if token_generator.check_token(user_object, token):
            return render(request, 'password_reset_confirm.html')
        else:
            messages.error(request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = User.objects.get(id=uid)
        token_generator = default_token_generator
        if not token_generator.check_token(user_object, token):
            messages.error(self.request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

        password1 = self.request.POST.get('new_password1')
        password2 = self.request.POST.get('new_password2')

        if password1 != password2:
            messages.error(self.request, "Passwords do not match")
            return render(request, 'password_reset_confirm.html')
        elif len(password1) < 8:
            messages.error(
                self.request, "Password must be atleast 8 characters long")
            return render(request, 'password_reset_confirm.html')
        elif password1.isdigit() or password2.isdigit() or password1.isalpha() or password2.isalpha():
            messages.error(
                self.request, "Passwords must have a mix of numbers and characters")
            return render(request, 'password_reset_confirm.html')
        else:
            token = kwargs['token']
            user_id_b64 = kwargs['uidb64']
            uid = urlsafe_base64_decode(user_id_b64).decode()
            user_object = User.objects.get(id=uid)
            user_object.set_password(password1)
            user_object.save()
            return HttpResponseRedirect('/password-reset-complete/')


class PasswordResetView(LoginRequiredMixin, View):
    template_name = 'password_reset.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(request, 'password_reset.html')

    def post(self, request, *args, **kwargs):
        user = User
        email = request.POST.get('email')
        email_template = "password_reset_email.html"
        user_qs = user.objects.filter(email=email)
        if len(user_qs) == 0:
            messages.error(request, 'Email does not exists')
            return render(request, 'password_reset.html')

        elif len(user_qs) == 1:
            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "On Demand"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }
            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL,
                      [email], fail_silently=False)
            return redirect('/password-reset-done/')
        else:

            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "E-receipt"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }

            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            print(email_body)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL,
                      [email], fail_silently=False)
            return redirect('/password-reset-done/')


class PasswordChangeView(LoginRequiredMixin, PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('adminpanel:dashboard')
    login_url = "adminpanel:login"

    # template_name = 'registration/password_change_form.html'
    title = ('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password changed successfully')
        return super().form_valid(form)


class PasswordChangeDoneView(LoginRequiredMixin, PasswordContextMixin, TemplateView):
    # template_name = 'registration/password_change_done.html'
    title = ('Password change successful')
    login_url = "adminpanel:login"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AddServiceProvider(LoginRequiredMixin, CreateView):
    template_name = 'Addserviceprovider.html'
    model = User
    form_class = AddServiceProviderForm
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(SubCategory.objects.all())
        print(Services.objects.all())
        return render(self.request, 'Addserviceprovider.html',
                      {'category': Category.objects.all(), 'sub_category': SubCategory.objects.all(),
                       'services': Services.objects.all(), 'form': self.form_class})

    def post(self, request, *args, **kwargs):
        # print(self.request.POST)
        full_name = self.request.POST['full_name']
        country_code = self.request.POST['country_code']
        phone_number = self.request.POST['phone_number']
        category = self.request.POST['category']
        sub_category = self.request.POST['sub_category']
        services = self.request.POST['services']
        email = self.request.POST['email']
        address = self.request.POST['address']
        password = self.request.POST['password']
        confirm_password = self.request.POST['confirm_password']
        # profile_pic = self.request.POST.get('profile_pic' or None)
        profile_pic = self.request.FILES.get('profile_pic' or None)
        print(self.request.FILES['profile_pic'])
        # print(type(self.request.FILES['profile_pic']))
        # print(profile_pic)
        # print(type(profile_pic))
        # print('Form', AddServiceProviderForm(self.request.POST))
        # form = AddServiceProviderForm(self.request.POST)
        # print('>>>>>>>>>>>>>>', form.fields['full_name'])
        # print('>>>>>>>>>>>>>>',form.full_name)
        # print('>>>>>>>>>>>>>>',form.cleaned_data['full_name'])
        try:
            user_obj = User.objects.get(Q(email=email) | Q(phone_number=phone_number))
            print(user_obj)
            messages.error(self.request, 'User with this email/phone number already exists')
            return render(self.request, self.template_name,
                          {'category': Category.objects.all(), 'form': self.form_class})
        except Exception as e:
            print(e)
            if password != confirm_password:
                messages.error(self.request, 'Password and Confirm Password did not match')
                return render(self.request, self.template_name,
                              {'category': Category.objects.all(), 'form': self.form_class})
            elif len(password) < 8:
                messages.error(self.request, 'Password must contain minimum of 8 characters')
                return render(self.request, self.template_name,
                              {'category': Category.objects.all(), 'form': self.form_class})
            elif password.isdigit() or password.isalpha():
                messages.error(self.request, 'Password must be a mix of character, numbers and special characters')
                return render(self.request, self.template_name,
                              {'category': Category.objects.all(), 'form': self.form_class})
            else:
                ServiceProvider.objects.create(
                    full_name=full_name,
                    country_code=country_code,
                    phone_number=phone_number,
                    category=Category.objects.get(id=category),
                    sub_category=SubCategory.objects.get(id=sub_category),
                    services=Services.objects.get(id=services),
                    email=email,
                    address=address,
                    password=password,
                    confirm_password=confirm_password,
                    profile_pic=profile_pic
                )
                user = User.objects.create(
                    full_name=full_name,
                    email=email,
                    country_code=country_code,
                    phone_number=phone_number,
                    is_provider=True,
                    # profile_pic=profile_pic
                )
                user.set_password(password)
                user.save()
                messages.success(self.request, 'Service provider added successfully')
                return redirect("adminpanel:service-provider-management")


class AddSubCategory(LoginRequiredMixin, CreateView):
    template_name = 'Add-SubCategory.html'
    form_class = SubCategoryForm
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'Add-SubCategory.html', {"category": Category.objects.all()})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        SubCategory.objects.create(
            category=Category.objects.get(id=self.request.POST['category']),
            sub_category_name=self.request.POST['sub_category_name'].lower(),
            sub_category_name_arabic=self.request.POST['sub_category_name_arabic'],
            sub_category_image=self.request.FILES.get('sub_category_image' or None),
        )
        messages.success(self.request, 'Sub Category added successfully')
        return redirect("adminpanel:sub-category-management")


class SubCategoryView(LoginRequiredMixin, ListView):
    template_name = 'Sub-Category.html'
    model = SubCategory
    login_url = "adminpanel:login"

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'Sub-Category.html')


class SubCategoryDetail(LoginRequiredMixin, DetailView):
    template_name = 'SubCategoryDetail.html'
    model = SubCategory
    login_url = "adminpanel:login"


class UpdateSubCategory(LoginRequiredMixin, UpdateView):
    template_name = 'update-subcategory.html'
    model = SubCategory
    form_class = SubCategoryForm
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'update-subcategory.html',
                      {'object': SubCategory.objects.get(id=kwargs['pk']), 'category': Category.objects.all()})

    def post(self, request, *args, **kwargs):
        sub_category_obj = SubCategory.objects.get(id=kwargs['pk'])
        sub_category_obj.category = Category.objects.get(id=self.request.POST['category'])
        sub_category_obj.sub_category_name = self.request.POST['sub_category_name'].lower()
        sub_category_obj.sub_category_name_arabic = self.request.POST['sub_category_name_arabic']
        sub_category_obj.sub_category_image = self.request.FILES.get('sub_category_image' or None)
        sub_category_obj.save()
        messages.success(self.request, "Sub Category updated successfully")
        return redirect("adminpanel:sub-category-management")


class SubAdminManagement(LoginRequiredMixin, ListView):
    template_name = 'sub-admin-management.html'
    model = User
    login_url = "adminpanel:login"

    # def get_queryset(self):
    #     return User.objects.filter(is_sub_admin=True)

    def get(self, request, *args, **kwargs):
        print(User.objects.filter(is_sub_admin=True))
        return render(self.request, 'sub-admin-management.html',
                      {'object_list': User.objects.filter(is_sub_admin=True)})


class AddSubAdmin(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'add-admin.html'
    form_class = SubAdminForm
    login_url = "adminpanel:login"

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        name = self.request.POST['full_name']
        email = self.request.POST['email']
        phone_number = self.request.POST['phone_number']
        password = self.request.POST['password']
        confirm_password = self.request.POST['confirm_password']
        access_rights = self.request.POST.getlist('access_rights')
        print(access_rights)
        try:
            user_obj = User.objects.get(Q(email=email) | Q(phone_number=phone_number))
            messages.error(self.request, 'User with this email/phone already exists')
            return render(self.request, 'add-admin.html')
        except Exception as e:
            print('Exception----->>>', e)
            if password == confirm_password:
                user = User.objects.create(
                    full_name=name,
                    email=email,
                    phone_number=phone_number,
                    is_sub_admin=True
                )
                user.set_password(password)
                for right in access_rights:
                    if '_'.join(right.lower().split()) == 'can_manage_user':
                        user.can_manage_user = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_order':
                        user.can_manage_order = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_provider':
                        user.can_manage_provider = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_category':
                        user.can_manage_category = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_sub_category':
                        user.can_manage_sub_category = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_services':
                        user.can_manage_services = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_subadmin':
                        user.can_manage_subadmin = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_top_services':
                        user.can_manage_top_services = True
                        user.save()
                    if '_'.join(right.lower().split()) == 'can_manage_coupons':
                        user.can_manage_coupons = True
                        user.save()
                messages.success(self.request, 'Sub Admin added successfully')
                return redirect("adminpanel:sub-admin-management")
            else:
                messages.success(self.request, 'Password and Confirm Password does not match')
                return render(self.request, 'add-admin.html')


class ServicesList(LoginRequiredMixin, ListView):
    model = Services
    template_name = 'services-list.html'
    login_url = "adminpanel:login"


class AddServices(LoginRequiredMixin, CreateView):
    model = Services
    template_name = 'add-services.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        return render(self.request, 'add-services.html',
                      {'category': Category.objects.all(), 'sub_category': SubCategory.objects.all()})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        category = self.request.POST['category']
        sub_category = self.request.POST['sub_category']
        service_name = self.request.POST['service_name']
        service_name_arabic = self.request.POST['service_name_arabic']
        field_1 = self.request.POST['field_1']
        field_2 = self.request.POST['field_2']
        field_3 = self.request.POST['field_3']
        field_4 = self.request.POST['field_4']
        base_price = self.request.POST['base_price']
        image_1 = self.request.FILES['image_1']
        image_2 = self.request.FILES['image_2']
        Services.objects.create(category=Category.objects.get(id=category),
                                sub_category=SubCategory.objects.get(id=sub_category),
                                service_name=service_name.lower(),
                                service_name_arabic=service_name_arabic,
                                image_1=image_1, image_2=image_2, field_1=field_1, field_2=field_2, field_3=field_3,
                                field_4=field_4, base_price=base_price)
        messages.success(self.request, 'Service added successfully')
        return redirect("adminpanel:services-list")


class UpdateService(LoginRequiredMixin, UpdateView):
    model = Services
    template_name = 'update-services.html'
    form_class = UpdateServiceForm
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        service_obj = Services.objects.get(id=kwargs['pk'])
        return render(self.request, 'update-services.html',
                      {'category': Category.objects.all(), 'sub_category': SubCategory.objects.all(),
                       'service_name': service_obj.service_name,
                       'service_name_arabic': service_obj.service_name_arabic, 'field1': service_obj.field_1,
                       'field2': service_obj.field_2, 'field3': service_obj.field_3, 'field4': service_obj.field_4})

    def post(self, request, *args, **kwargs):
        # print(self.form_class.is_valid())
        print(self.request.POST)
        print(self.request.FILES['image_1'])
        print(self.request.FILES['image_2'])
        service_obj = Services.objects.get(id=kwargs['pk'])
        service_obj.category = Category.objects.get(id=self.request.POST['category'])
        service_obj.sub_category = SubCategory.objects.get(id=self.request.POST['sub_category'])
        service_obj.service_name = self.request.POST['service_name']
        service_obj.service_name_arabic = self.request.POST['service_name_arabic']
        service_obj.image_1 = self.request.FILES['image_1']
        service_obj.image_2 = self.request.FILES['image_2']
        service_obj.field_1 = self.request.POST['field_1']
        service_obj.field_2 = self.request.POST['field_2']
        service_obj.field_3 = self.request.POST['field_3']
        service_obj.field_4 = self.request.POST['field_4']
        service_obj.save()
        messages.success(self.request, 'Service updated successfully')
        return redirect("adminpanel:services-list")


class TopServicesList(LoginRequiredMixin, ListView):
    model = TopServices
    template_name = 'top-services-list.html'
    login_url = "adminpanel:login"

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, "top-services-list.html")


class TopServicesView(LoginRequiredMixin, CreateView):
    model = TopServices
    template_name = 'top-services.html'
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        print(Services.objects.all())
        print(TopServices.objects.all())
        checked = []
        unchecked = []
        for service in Services.objects.all():
            if service in [x.service for x in TopServices.objects.all()]:
                checked.append(service)
            else:
                unchecked.append(service)
        return render(self.request, 'top-services.html',
                      {'checked': checked, 'unchecked': unchecked})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        print(self.request.POST.getlist('service_name'))
        for obj in self.request.POST.getlist('service_name'):
            print(obj)
            try:
                TopServices.objects.get(service=Services.objects.get(id=obj))
                print('TRY BLOCK ', TopServices.objects.get(service=Services.objects.get(id=obj)))
            except Exception as e:
                print('Exception---->>', e)
                TopServices.objects.create(service=Services.objects.get(id=obj))
        messages.success(self.request, "Top services added successfully")
        return redirect("adminpanel:top-services-list")


class DeleteTopService(LoginRequiredMixin, DeleteView):
    model = TopServices
    template_name = 'delete-top-services.html'
    success_url = reverse_lazy("adminpanel:top-services-list")
    login_url = "adminpanel:login"


# class BlockUser(View):
#     model = User
#
#     def get(self, request, *args, **kwargs):
#         print(kwargs['pk'])
#         messages.info(self.request, "User blocked successfully")
#         return redirect("adminpanel:user-management")


class NotificationCount(LoginRequiredMixin, View):
    model = AdminNotifications
    login_url = "adminpanel:login"

    def get(self, request, *args, **kwargs):
        notification_count = AdminNotifications.objects.filter(read=False).count()
        return HttpResponse(notification_count)


class InquiryView(LoginRequiredMixin, ListView):
    template_name = 'inquiry.html'
    model = GeneralInquiry
    login_url = "adminpanel:login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        inquiries = Inquiry.objects.all()
        context['inquiries'] = inquiries
        return context


class UserProviderRegistrations(LoginRequiredMixin, ListView):
    template_name = 'user-provider-registration.html'
    model = ProviderRegistration
    login_url = "adminpanel:login"

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'inquiry.html')


class StaticPrivacyPolicyForAppStores(View):
    template_name = 'privacy-policy-for-apps.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'privacy-policy-for-apps.html')


class TermsAndConditionForAppStores(View):
    template_name = 'terms-condition-for-apps.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'privacy-policy-for-apps.html')


class GetGstView(View):
    model = Gst
    template_name = 'gst.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'gst.html', {'object': Gst.objects.all()})


class UpdateGstView(View):
    model = Gst
    template_name = 'update-gst.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'update-gst.html', {'gst': Gst.objects.all()[0]})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        print(kwargs)
        print(args)
        obj = Gst.objects.get(id=kwargs['pk'])
        obj.gst = self.request.POST['gst']
        obj.save()
        return redirect("adminpanel:get-gst")


class UpdateOrder(LoginRequiredMixin, View):
    model = Booking
    template_name = "update-order.html"

    def get(self, request, *args, **kwargs):
        print(kwargs)
        booking_obj = Booking.objects.get(id=kwargs['pk'])
        return render(self.request, 'update-order.html', {'object': booking_obj, 'services': Services.objects.all()})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        booking_obj = Booking.objects.get(id=kwargs['pk'])
        service_obj = Services.objects.get(id=self.request.POST['service'])
        booking_obj.service = service_obj
        booking_obj.time = self.request.POST['time']
        booking_obj.admin_percent = self.request.POST['admin_percent']
        booking_obj.sub_total = self.request.POST['sub_total']
        booking_obj.total = self.request.POST['total']
        booking_obj.additional_fees = self.request.POST['additional_fees']
        booking_obj.requirement = self.request.POST['requirement']
        booking_obj.address = self.request.POST['address']
        from datetime import datetime
        x = datetime.strptime(self.request.POST['date'], "%B %d, %Y")
        print('-----', x)
        booking_obj.date = x.strftime("%Y-%m-%d")
        booking_obj.save()
        messages.success(self.request, 'Order updated successfully')
        return redirect("adminpanel:order-management")


class OrderCanceledByAdmin(View):
    model = Booking
    template_name = 'canceled-order.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'canceled-order.html',
                      {'object': Booking.objects.filter(is_canceled_by_admin=True).order_by('-id')})
