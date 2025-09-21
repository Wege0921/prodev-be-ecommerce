from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # to be extended, I will use role based users
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
