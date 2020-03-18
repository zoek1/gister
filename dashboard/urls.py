from django.urls import re_path, path

from dashboard.views import gist_details, all_gists

urlpatterns = [
    re_path(r'^(?P<gist_id>[\w\d]+)', gist_details, name='gist-details'),
    path('', all_gists, name='all-gists')
]