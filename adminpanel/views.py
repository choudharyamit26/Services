from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, DetailView, UpdateView, FormView, TemplateView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import User


# Create your views here.

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
        return render(self.request, 'user-management.html')


class ServiceProviderManagementView(View):
    template_name = 'service-provider-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'service-provider-management.html')


class SubAdminManagementView(View):
    template_name = 'sub-admin-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'sub-admin-management.html')


class CategoryView(View):
    template_name = 'Category.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'Category.html')


class OrderManagementView(View):
    template_name = 'order-management.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'order-management.html')


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

    def get(self, request, *args, **kwargs):
        return render(self.request, 'offer.html')


class FinanceManagementView(View):
    template_name = 'finance.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'finance.html')


class StaticContentManagementView(View):
    template_name = 'static.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'static.html')


class NotificationManagementView(View):
    template_name = 'notification.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'notification.html')


class AdminProfileView(View):
    template_name = 'myprofile.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'myprofile.html')


class ChangePasswordView(View):
    template_name = 'changePassword.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'changePassword.html')


class UserDetailView(View):
    template_name = 'userdetail.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'userdetail.html')


class ServiceDetailView(View):
    template_name = 'servicedetails.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'servicedetails.html')


class SubAdminDetail(View):
    template_name = 'view-admin.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'view-admin.html')


class EditSubAdmin(View):
    template_name = 'edit-admin.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, 'edit-admin.html')


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
