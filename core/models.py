# For creation of custom designed users.
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):  # Extending AbstractUser class.
    # Redefining email field by applying "unique" constraint to it.
    email = models.EmailField(unique=True)
