from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DonorProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'phone_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )

class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'is_available', 'last_donation_date']
    list_filter = ['blood_group', 'is_available']
    search_fields = ['user__username', 'blood_group']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DonorProfile, DonorProfileAdmin)
