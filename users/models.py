from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # to be extended, 
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username
