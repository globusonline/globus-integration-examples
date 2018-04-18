from django.db import models
from django.contrib.auth.models import User

class AccessToken(models.Model):
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=255)
    dependent_token = models.CharField(max_length=255)
