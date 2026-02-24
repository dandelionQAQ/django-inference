from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils.io import avatar_upload_to


class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)  # 头像
    bio = models.TextField(max_length=512, blank=True, null=True)  # 简介
