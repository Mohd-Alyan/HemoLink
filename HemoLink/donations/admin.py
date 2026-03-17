from django.contrib import admin
from .models import BloodBank, BloodRequest, Notification, Pledge, DonationHistory

class BloodBankAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'latitude', 'longitude']
    search_fields = ['name', 'address']

class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group_required', 'urgency_level', 'status', 'requested_by', 'created_at']
    list_filter = ['blood_group_required', 'urgency_level', 'status']
    search_fields = ['patient_name', 'location']
    date_hierarchy = 'created_at'

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_read', 'created_at', 'related_request']
    list_filter = ['is_read']
    date_hierarchy = 'created_at'

class PledgeAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_request', 'created_at']
    list_filter = ['created_at']

class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_group', 'units_donated', 'location', 'donated_at']
    list_filter = ['blood_group', 'donated_at']
    search_fields = ['donor__username', 'location']
    date_hierarchy = 'donated_at'

admin.site.register(BloodBank, BloodBankAdmin)
admin.site.register(BloodRequest, BloodRequestAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Pledge, PledgeAdmin)
admin.site.register(DonationHistory, DonationHistoryAdmin)
