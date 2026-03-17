from django.db import models
from accounts.models import CustomUser

class BloodBank(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class BloodRequest(models.Model):
    URGENCY_CHOICES = (
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
    )

    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=255)
    blood_group_required = models.CharField(max_length=10)
    units_required = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group_required} ({self.status})"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


class Pledge(models.Model):
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pledges')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='pledges')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('donor', 'blood_request')

    def __str__(self):
        return f"{self.donor.username} pledged for {self.blood_request}"


class DonationHistory(models.Model):
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donation_history')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    blood_group = models.CharField(max_length=10)
    units_donated = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    donated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Donation histories"

    def __str__(self):
        return f"{self.donor.username} donated {self.blood_group} on {self.donated_at.strftime('%Y-%m-%d')}"
