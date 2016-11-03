from django.db import models


USER_TYPE_CHOICES = (
    ('0', 'director'),
    ('1', 'manager'),
    ('2', 'employee'),
)
# Create your models here.
class User(models.Model):
    firstName=models.CharField(max_length=200)
    lastName=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    role=models.CharField(max_length=1,choices=USER_TYPE_CHOICES)
    password=models.CharField(max_length=200)
    username=models.CharField(max_length=200)


