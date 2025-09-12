from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

USER_TYPE_CHOICES = [
    ('MEMBER', 'Member'),
    ('MANAGER', 'Manager'),
]

class User(AbstractUser):
    user_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)  
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='MEMBER')
    national_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    kra_pin = models.CharField(max_length=100, unique=True, null=True, blank=True)
    next_of_kin_name = models.CharField(max_length=100, null=True, blank=True)
    next_of_kin_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = []  

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
