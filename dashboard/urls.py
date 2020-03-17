from django.urls import re_path

from dashboard.views import gist_details

urlpatterns = [
    re_path(r'^(?P<gist_id>[\w\d]+)', gist_details, name='gist-details'),
]