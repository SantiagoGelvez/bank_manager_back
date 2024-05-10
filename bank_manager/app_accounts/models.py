import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, verbose_name='UUID')
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Phone Number')

# Create your models here.
