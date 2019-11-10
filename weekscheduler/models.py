from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    day_of_week = models.PositiveSmallIntegerField(verbose_name='day of week', default=0, validators=[
        MinValueValidator(limit_value=0),
        MaxValueValidator(limit_value=6)
    ])
    start_time = models.TimeField(verbose_name='start time')
    finish_time = models.TimeField(verbose_name='finish time', null=True)
    title = models.TextField(verbose_name='title')
    description = models.TextField(verbose_name='description', null=True, blank=True)
    created_ts = models.DateTimeField(verbose_name='created timestamp', auto_now_add=True)
    modified_ts = models.DateTimeField('modified timestamp', auto_now=True)

    owner = models.ForeignKey(User, verbose_name='owner', related_name='events', on_delete=models.CASCADE)

    def clean(self):
        if self.start_time >= self.finish_time:
            raise ValidationError(_('Starting time of event must be lesser than its finish time.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('day_of_week', 'start_time', 'finish_time', 'title',)
        unique_together = ('owner', 'day_of_week', 'start_time', 'title')
