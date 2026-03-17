from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('donor', 'Donor'),
        ('patient', 'Patient'),
        ('hospital', 'Hospital'),
        ('blood_bank', 'Blood Bank'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class DonorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=5)
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True, help_text="Available for emergency blood donation")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.blood_group}"
