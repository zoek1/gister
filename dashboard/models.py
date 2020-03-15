from django.contrib.postgres.fields import ArrayField
from django.db import models


class Gist(models.Model):
    VISIBILITY_LEVELS = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('non_listed', 'No Listed')
    )
    EXPIRATION_OPTIONS = (
        ('10_MINUTES', '10 Minutes'),
        ('1_HOUR', '1 Hour'),
        ('1_DAY', '1 Day'),
        ('1_WEEk', '1 Week'),
        ('2_WEEk', '2 Weeks'),
        ('1_MONTH', '1 Month'),
        ('6_MONTH', '6 Month'),
        ('1_YEAR', '1 Year'),
    )
    visibility = models.CharField(max_length=30, choices=VISIBILITY_LEVELS)
    parent = models.ForeignKey('dashboard.Gist', null=True, blank=True, on_delete=models.CASCADE)
    sia_path = models.CharField(max_length=120, blank=True, default='', db_index=True)
    uuid = models.CharField(max_length=120, blank=True, default='', db_index=True)
    skynet_url = models.CharField(max_length=120, null=True, blank=True)
    description = models.CharField(max_length=220, null=True, blank=True)
    expiration = models.CharField(max_length=30, choices=EXPIRATION_OPTIONS)
    categories = ArrayField(models.CharField(max_length=40, blank=True), null=True, name='categories')
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user_address = models.CharField(max_length=120, blank=True, default='')


class File(models.Model):
    sia_path = models.CharField(max_length=120, blank=True, default='')
    skynet_url = models.CharField(max_length=120, null=True, blank=True)
    file_name = models.CharField(max_length=120, null=True, blank=True)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user_address = models.CharField(max_length=120)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)