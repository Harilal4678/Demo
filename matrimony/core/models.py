from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    religion = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class PartnerPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    preferred_religion = models.CharField(max_length=100, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    preferred_profession = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
