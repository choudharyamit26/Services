from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import *
from src.models import AppUser,Settings,UserPromoCode


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'full_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'),
         {'fields': ('full_name',)}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'confirm_password')
        }),
    )


admin.site.register(User)
admin.site.register(ServiceProvider)
admin.site.register(Category)
admin.site.register(AppUser)
admin.site.register(UserPromoCode)
admin.site.register(Settings)
admin.site.register(Services)
admin.site.register(TopServices)
