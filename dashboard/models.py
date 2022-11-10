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
    path = models.CharField(max_length=120, blank=True, default='', db_index=True)
    uuid = models.CharField(max_length=120, blank=True, default='', db_index=True)
    cid = models.CharField(max_length=120, null=True, blank=True)
    description = models.CharField(max_length=220, null=True, blank=True)
    expiration = models.CharField(max_length=30, choices=EXPIRATION_OPTIONS)
    categories = ArrayField(models.CharField(max_length=40, blank=True), null=True, name='categories')
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_address = models.CharField(max_length=120, blank=True, default='')
    active = models.BooleanField(default=True)
    manifest_cid = models.CharField(max_length=120, null=True, blank=True)
    manifest_path = models.CharField(max_length=120, null=True, blank=True)

    def preview_file(self):
        file = self.file_set.first()
        return file

    def get_default_dict(self):
        response = {
            'id': self.uuid,
            'visibility': self.visibility,
            'cid': self.cid,
            'description': self.description,
            'expiration': self.expiration,
            'categories': self.categories,
            'user_address': self.user_address,
            'parent': self.parent,
            'package_path': self.path,
            'active': self.active,
            'created': self.created.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'manifest_cid': self.manifest_cid
        }

        files = []
        ready = True
        for file in self.file_set.all():
            files.append({
                'path': file.path,
                'cid': file.cid,
                'file_name': file.file_name,
                'created': file.created.isoformat(),
                'updated_at': file.updated_at.isoformat(),
            })

            if not file.cid:
                ready = False

        response['ready'] = ready
        response['files'] = files

        return response

    def get_categories(self):
        file_categories = [file.syntax for file in self.file_set.all() if file.syntax]

        return {*file_categories, *self.categories}


class File(models.Model):
    path = models.CharField(max_length=120, blank=True, default='')
    cid = models.CharField(max_length=120, null=True, blank=True)
    file_name = models.CharField(max_length=120, null=True, blank=True)
    gist = models.ForeignKey(Gist, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    syntax = models.CharField(max_length=40, null=True, blank=True)

    def get_cid_url(self):
        return f'https://{self.cid}.ipfs.w3s.link'

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