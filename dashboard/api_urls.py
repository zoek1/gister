from django.urls import re_path, path

from dashboard.views import create_gist, get_gist

urlpatterns = [
    path(r'<gist_id>', get_gist, name='gist-action'),
    path(r'/', create_gist, name='gists-actions'),
]