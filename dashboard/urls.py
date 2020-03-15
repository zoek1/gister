from django.urls import re_path

from dashboard.views import gist_details

urlpatterns = [
    re_path(r'^(?P<path>[\w\d]+)', gist_details, 'gist-details')
]