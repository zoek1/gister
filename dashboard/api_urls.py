from django.urls import re_path

from dashboard.views import create_gist

urlpatterns = [
    re_path(r'', create_gist, name='api-gists'),
    re_path(r'(?P<path>[\w\d]+)', create_gist, name='api-gist')
]