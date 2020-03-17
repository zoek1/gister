from django.urls import re_path

from dashboard.views import create_gist, get_gist

urlpatterns = [
    re_path(r'(?P<gist_id>[\w\d]+)', get_gist, name='api-gist'),
    re_path(r'', create_gist, name='api-gists'),
]