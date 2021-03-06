from django.contrib.postgres.fields import ArrayField
from django.db import models


class Gist(models.Model):
    VISIBILITY_LEVELS = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('non_listed', 'No Listed')
    )
    EXPIRATION_OPTIONS = (
        ('NEVER', 'Never'),
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
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_address = models.CharField(max_length=120, blank=True, default='')
    active = models.BooleanField(default=True)
    skynet_manifest_url = models.CharField(max_length=120, null=True, blank=True)
    sia_manifest_path = models.CharField(max_length=120, null=True, blank=True)

    def preview_file(self):
        file = self.file_set.first()
        return file

    def get_default_dict(self):
        response = {
            'id': self.uuid,
            'visibility': self.visibility,
            'skynet_url': self.skynet_url,
            'description': self.description,
            'expiration': self.expiration,
            'categories': self.categories,
            'user_address': self.user_address,
            'parent': self.parent,
            'package_path': self.sia_path,
            'active': self.active,
            'created': self.created.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'manifest_url': self.skynet_manifest_url
        }

        files = []
        ready = True
        for file in self.file_set.all():
            files.append({
                'sia_path': file.sia_path,
                'skynet_url': file.skynet_url,
                'file_name': file.file_name,
                'created': file.created.isoformat(),
                'updated_at': file.updated_at.isoformat(),
            })

            if not file.skynet_url:
                ready = False

        response['ready'] = ready
        response['files'] = files

        return response

    def get_categories(self):
        file_categories = [file.syntax for file in self.file_set.all() if file.syntax]

        return {*file_categories, *self.categories}


class File(models.Model):
    sia_path = models.CharField(max_length=120, blank=True, default='')
    skynet_url = models.CharField(max_length=120, null=True, blank=True)
    file_name = models.CharField(max_length=120, null=True, blank=True)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    syntax = models.CharField(max_length=40, null=True, blank=True)

    def get_skynet_url(self):
        return f'https://siasky.net/{self.skynet_url.lstrip("sia://")}'

    def get_lang(self):
        if self.syntax:
            return self.syntax

        if len(self.gist.categories) > 0:
            return self.gist.categories[0]

        return 'plaintext'

class Follow(models.Model):
    user_address = models.CharField(max_length=120)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)