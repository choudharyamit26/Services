from django import forms
from .models import User, ServiceProvider, Category


class AddServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = (
        'full_name', 'country_code', 'phone_number', 'category', 'address', 'email', 'password', 'confirm_password')


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
