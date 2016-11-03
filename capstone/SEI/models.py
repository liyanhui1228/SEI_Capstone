from django.db import models
from django.contrib.auth.models import User

USER_TYPE_CHOICES = (
    ('0', 'director'),
    ('1', 'manager'),
    ('2', 'employee'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    activation_key = models.CharField(max_length=255)
    role = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)



