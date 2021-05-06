from django import forms
from .models import User, ServiceProvider, Category, SubCategory, Services
from src.models import Booking, OffersAndDiscount, ContactUs, AboutUs, TermsAndCondition, PrivacyPolicy
from ckeditor.widgets import CKEditorWidget


class AddServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = (
            'full_name', 'country_code', 'phone_number', 'category', 'sub_category', 'services', 'address', 'email',
            'password', 'confirm_password')


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = '__all__'


class SubAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone_number', 'password', 'confirm_password')


class UpdateServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = '__all__'


class AssignServiceProviderForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('id', 'service_provider')


class UpdateOfferForm(forms.ModelForm):
    class Meta:
        model = OffersAndDiscount
        fields = ('coupon_code', 'percent')


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('phone_number', 'email')


class AboutUsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    content_arabic = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = AboutUs
        fields = ('content', 'content_arabic')


class TermsAndConditionForm(forms.ModelForm):
    terms = forms.CharField(widget=CKEditorWidget())
    terms_arabic = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = TermsAndCondition
        fields = ('terms', 'terms_arabic')


class PrivacyPolicyForm(forms.ModelForm):
    policy = forms.CharField(widget=CKEditorWidget())
    policy_arabic = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PrivacyPolicy
        fields = ('policy', 'policy_arabic')
