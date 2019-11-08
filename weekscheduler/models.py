from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    day_of_week = models.PositiveSmallIntegerField(verbose_name='day of week', default=0)
    start_time = models.TimeField(verbose_name='start time')
    finish_time = models.TimeField(verbose_name='finish time')
    title = models.TextField(verbose_name='title')
    description = models.TextField(verbose_name='description')
    created_ts = models.DateTimeField(verbose_name='created timestamp', auto_now_add=True)
    modified_ts = models.DateTimeField('modified timestamp', auto_now=True)

    owner = models.ForeignKey(User, verbose_name='owner', related_name='events', on_delete=models.CASCADE)


