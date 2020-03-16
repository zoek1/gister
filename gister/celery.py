import os
from datetime import timedelta
from django.utils import timezone

from celery import Celery
from celery.schedules import crontab
from celery.task import periodic_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gister.settings')
app = Celery('gister')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="validate_expiration",
    ignore_result=True
)
def check_expiration(*args, **kwargs):
    from dashboard.models import Gist
    for gist in Gist.objects.filter(active=True).exclude(expiration='never'):
        print(f'ID {gist.id} - {gist.sia_path}')
        if gist.expiration == '10_MINUTES' and gist.created + timedelta(minutes=10) <= timezone.now():
            print('10 minutes')
            gist.active = False

        if gist.expiration == '1_HOUR' and gist.created + timedelta(hours=1) <= timezone.now():
            print('1 HOUR')
            gist.active = False

        if gist.expiration == '1_DAY' and  gist.created + timedelta(hours=24) <= timezone.now():
            print('1 Day')
            gist.active = False

        if gist.expiration == '1_WEEk' and gist.created + timedelta(days=7) <= timezone.now():
            print('1 Week')
            gist.active = False

        if gist.expiration == '2_WEEk' and gist.created + timedelta(days=14) <= timezone.now():
            print('2 Week')
            gist.active = False

        if gist.expiration == '1_MONTH' and gist.created + timedelta(days=30) <= timezone.now():
            print('1 Month')
            gist.active = False

        if gist.expiration == '6_MONTH' and gist.created + timedelta(days=30 * 6) <= timezone.now():
            print('6 Month')
            gist.active = False

        if gist.expiration == '1_YEAR' and gist.created + timedelta(days=365) <= timezone.now():
            print('1 Year')
            gist.active = False

        gist.save()