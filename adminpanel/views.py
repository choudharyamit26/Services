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

from .forms import AddServiceProviderForm, AddCategoryForm, SubCategoryForm, SubAdminForm, UpdateServiceForm, \
    AssignServiceProviderForm, UpdateOfferForm
from .models import User, Category, ServiceProvider, SubCategory, Services, TopServices, AdminNotifications
from src.models import Booking, OffersAndDiscount, AppUser, GeneralInquiry, Inquiry, ProviderRegistration
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
                if user_object.is_superuser:
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


class Dashboard(View):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'dashboard.html')


class UserManagementView(View):
    template_name = 'user-management.html'

    def get(self, request, *args, **kwargs):
        users = AppUser.objects.all()
        # users = User.objects.filter(is_provider=False)
        # print(users)
        # print(User.objects.all())
        # print(User.objects.filter(is_provider=False))
        return render(self.request, 'user-management.html', {'object_list': users})


class ServiceProviderManagementView(View):
    template_name = 'service-provider-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'service-provider-management.html', {'object_list': ServiceProvider.objects.all()})


# class SubAdminManagementView(View):
#     template_name = 'sub-admin-management.html'
#
#     def get(self, request, *args, **kwargs):
#         return render(self.request, 'sub-admin-management.html')


class CategoryView(ListView):
    template_name = 'Category.html'
    model = Category

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'Category.html')


class AddCategoryView(CreateView):
    template_name = 'addCategory.html'
    model = Category
    form_class = AddCategoryForm

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        # image = self.request.POST.get('category_image' or None)
        image = self.request.FILES.get('category_image' or None)
        print(image)
        print(type(image))
        category_name = self.request.POST['category_name']
        Category.objects.create(
            category_image=image,
            category_name=category_name.lower()
        )
        messages.success(self.request, 'Category added successfully')
        return redirect("adminpanel:category-management")


class CategoryDetail(DetailView):
    template_name = 'categoryDetails.html'
    model = Category


class OrderManagementView(ListView):
    model = Booking
    template_name = 'order-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'order-management.html',
                      {'object_list': Booking.objects.all().exclude(status='Rejected'),
                       'service_provider': ServiceProvider.objects.all()})


class RejectedOrderView(ListView):
    model = Booking
    template_name = 'rejected-order-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'rejected-order-management.html',
                      {'object_list': Booking.objects.filter(status='Rejected')})


class AssignServiceProvider(CreateView):
    model = Booking
    template_name = 'order-management.html'
    form_class = AssignServiceProviderForm

    def post(self, request, *args, **kwargs):
        print('From Assign Service Provider', self.request.POST)
        order = self.request.POST['orderId']
        service_provider_id = self.request.POST['serviceProviderId']
        order_obj = Booking.objects.get(id=order)
        order_obj.service_provider = ServiceProvider.objects.get(id=service_provider_id)
        order_obj.save()
        service_provider_device_type = order_obj.service_provider.device_type
        service_provider_device_token = order_obj.service_provider.device_token
        if service_provider_device_type == 'android':
            data_message = {
                "title": "New Message",
                "body": f"You have received a new service request for order with order ID {order_obj.id}"
            }
            respo = send_to_one(service_provider_device_token, data_message)
            print(respo)
        else:
            title = "New Message"
            body = f"You have received a new service request for order with order ID {order_obj.id}"
            # message_type = "NewMessage"
            # sound = 'notifications.mp3'
            respo = send_another(service_provider_device_token, title, body)
            print(respo)
        messages.success(self.request, 'Service provider assigned successfully')
        return redirect("adminpanel:order-management")


class SendQuoteView(CreateView):
    model = Booking
    template_name = 'order-management.html'

    def post(self, request, *args, **kwargs):
        print('>>>>>>>>>>>>>>>>>>>>>', self.request.POST)
        order_obj = Booking.objects.get(id=self.request.POST['orderId'])
        order_obj.quote = self.request.POST['quote']
        order_obj.save()
        user_device_type = order_obj.user.device_type
        user_device_token = order_obj.user.device_token
        if user_device_type == 'android':
            data_message = {
                "title": "New Message",
                "body": f"You have received a quote for order with order ID {order_obj.id}"
            }
            respo = send_to_one(user_device_token, data_message)
            print(respo)
        else:
            title = "New Message"
            body = f"You have received a quote for order with order ID {order_obj.id}"
            # message_type = "NewMessage"
            # sound = 'notifications.mp3'
            respo = send_another(user_device_token, title, body)
            print(respo)
        return redirect("adminpanel:order-management")


class VerificationManagementView(View):
    template_name = 'verification.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'verification.html')


class WorkerManagementView(View):
    template_name = 'worker.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'worker.html')


class OfferManagementView(View):
    template_name = 'offer.html'
    model = OffersAndDiscount

    def get(self, request, *args, **kwargs):
        return render(self.request, 'offer.html', {'object_list': OffersAndDiscount.objects.all()})


class OfferDetailView(DetailView):
    template_name = 'viewoffer.html'
    model = OffersAndDiscount


class DeleteOfferView(DeleteView):
    template_name = 'delete-offer.html'
    model = OffersAndDiscount
    success_url = reverse_lazy("adminpanel:offer-management")


class UpdateOfferView(UpdateView):
    template_name = 'update-coupon.html'
    model = OffersAndDiscount
    form_class = UpdateOfferForm

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        offer_obj = OffersAndDiscount.objects.get(id=kwargs['pk'])
        offer_obj.coupon_code = (self.request.POST['coupon_code']).upper()
        offer_obj.percent = self.request.POST['percent']
        offer_obj.save()
        messages.success(self.request, "Offer updated successfully")
        return redirect("adminpanel:offer-management")


class AddOffers(CreateView):
    template_name = 'update-coupon.html'
    model = OffersAndDiscount
    form_class = UpdateOfferForm

    def post(self, request, *args, **kwargs):
        coupon_code = self.request.POST['coupon_code']
        OffersAndDiscount.objects.create(coupon_code=coupon_code.upper(), percent=self.request.POST['percent'])
        messages.success(self.request, 'Offer added successfully')
        return redirect("adminpanel:offer-management")


class FinanceManagementView(View):
    template_name = 'finance.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'finance.html')


class StaticContentManagementView(View):
    template_name = 'static.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'static.html')


class NotificationManagementView(ListView):
    template_name = 'notification.html'
    model = AdminNotifications
    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'notification.html')


class ReadNotificationView(View):
    model = AdminNotifications

    def get(self, request, *args, **kwargs):
        notifications = AdminNotifications.objects.filter(read=False)
        for notification in notifications:
            notification.read = True
            notification.save()
        return HttpResponse('Read all notification')


class AdminProfileView(View):
    template_name = 'myprofile.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'myprofile.html')


class ChangePasswordView(View):
    template_name = 'changePassword.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'changePassword.html')


class UserDetailView(DetailView):
    template_name = 'userdetail.html'
    model = User

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'userdetail.html')


class ServiceProviderDetailView(DetailView):
    template_name = 'servicedetails.html'
    model = ServiceProvider

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'servicedetails.html')


class SubAdminDetail(View):
    template_name = 'view-admin.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'view-admin.html')


class EditSubAdmin(View):
    template_name = 'edit-admin.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'edit-admin.html', {'object': User.objects.get(id=kwargs['pk'])})

    def post(self, request, *args, **kwargs):
        name = self.request.POST['full_name']
        email = self.request.POST['email']
        phone_number = self.request.POST['phone_number']
        # password = self.request.POST['password']
        # confirm_password = self.request.POST['confirm_password']
        access_rights = self.request.POST.getlist('access_rights')
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
        messages.success(self.request, 'Sub Admin edited successfully')
        return redirect("adminpanel:sub-admin-management")


class PasswordResetConfirmView(View):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

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


class PasswordResetView(View):
    template_name = 'password_reset.html'

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


class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('adminpanel:dashboard')

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


class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    # template_name = 'registration/password_change_done.html'
    title = ('Password change successful')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AddServiceProvider(CreateView):
    template_name = 'Addserviceprovider.html'
    model = User
    form_class = AddServiceProviderForm

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


class AddSubCategory(CreateView):
    template_name = 'Add-SubCategory.html'
    form_class = SubCategoryForm

    def get(self, request, *args, **kwargs):
        return render(self.request, 'Add-SubCategory.html', {"category": Category.objects.all()})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        SubCategory.objects.create(
            category=Category.objects.get(id=self.request.POST['category']),
            sub_category_name=self.request.POST['sub_category_name'].lower(),
            sub_category_image=self.request.FILES.get('sub_category_image' or None),
        )
        messages.success(self.request, 'Sub Category added successfully')
        return redirect("adminpanel:sub-category-management")


class SubCategoryView(ListView):
    template_name = 'Sub-Category.html'
    model = SubCategory

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'Sub-Category.html')


class SubCategoryDetail(DetailView):
    template_name = 'SubCategoryDetail.html'
    model = SubCategory


class SubAdminManagement(ListView):
    template_name = 'sub-admin-management.html'
    model = User

    # def get_queryset(self):
    #     return User.objects.filter(is_sub_admin=True)

    def get(self, request, *args, **kwargs):
        print(User.objects.filter(is_sub_admin=True))
        return render(self.request, 'sub-admin-management.html',
                      {'object_list': User.objects.filter(is_sub_admin=True)})


class AddSubAdmin(CreateView):
    model = User
    template_name = 'add-admin.html'
    form_class = SubAdminForm

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
                messages.success(self.request, 'Sub Admin added successfully')
                return redirect("adminpanel:sub-admin-management")
            else:
                messages.success(self.request, 'Password and Confirm Password does not match')
                return render(self.request, 'add-admin.html')


class ServicesList(ListView):
    model = Services
    template_name = 'services-list.html'


class AddServices(CreateView):
    model = Services
    template_name = 'add-services.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'add-services.html',
                      {'category': Category.objects.all(), 'sub_category': SubCategory.objects.all()})

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        category = self.request.POST['category']
        sub_category = self.request.POST['sub_category']
        service_name = self.request.POST['service_name']
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
                                image_1=image_1, image_2=image_2, field_1=field_1, field_2=field_2, field_3=field_3,
                                field_4=field_4, base_price=base_price)
        messages.success(self.request, 'Service added successfully')
        return redirect("adminpanel:services-list")


class UpdateService(UpdateView):
    model = Services
    template_name = 'update-services.html'
    form_class = UpdateServiceForm

    def get(self, request, *args, **kwargs):
        service_obj = Services.objects.get(id=kwargs['pk'])
        return render(self.request, 'update-services.html',
                      {'category': Category.objects.all(), 'sub_category': SubCategory.objects.all(),
                       'service_name': service_obj.service_name})

    def post(self, request, *args, **kwargs):
        # print(self.form_class.is_valid())
        print(self.request.POST)
        print(self.request.FILES['image_1'])
        print(self.request.FILES['image_2'])
        service_obj = Services.objects.get(id=kwargs['pk'])
        service_obj.category = Category.objects.get(id=self.request.POST['category'])
        service_obj.sub_category = SubCategory.objects.get(id=self.request.POST['sub_category'])
        service_obj.service_name = self.request.POST['service_name']
        service_obj.image_1 = self.request.FILES['image_1']
        service_obj.image_2 = self.request.FILES['image_2']
        service_obj.save()
        messages.success(self.request, 'Service updated successfully')
        return redirect("adminpanel:services-list")


class TopServicesList(ListView):
    model = TopServices
    template_name = 'top-services-list.html'

    # def get(self, request, *args, **kwargs):
    #     return render(self.request, "top-services-list.html")


class TopServicesView(CreateView):
    model = TopServices
    template_name = 'top-services.html'

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


class DeleteTopService(DeleteView):
    model = TopServices
    template_name = 'delete-top-services.html'
    success_url = reverse_lazy("adminpanel:top-services-list")


class BlockUser(View):
    model = User

    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        messages.info(self.request, "User blocked successfully")
        return redirect("adminpanel:user-management")


class NotificationCount(View):
    model = AdminNotifications

    def get(self, request, *args, **kwargs):
        notification_count = AdminNotifications.objects.filter(read=False).count()
        return HttpResponse(notification_count)


class InquiryView(ListView):
    template_name = 'inquiry.html'
    model = GeneralInquiry

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        inquiries = Inquiry.objects.all()
        context['inquiries'] = inquiries
        return context


class UserProviderRegistrations(ListView):
    template_name = 'user-provider-registration.html'
    model = ProviderRegistration
    # def get(self, request, *args, **kwargs):
    #     return render(self.request, 'inquiry.html')
