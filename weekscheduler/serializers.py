from weekscheduler import models
from rest_framework import serializers


class EventHyperLinkedSerializer(serializers.HyperlinkedModelSerializer):
    created_ts = serializers.ReadOnlyField()
    modified_ts = serializers.ReadOnlyField()

    class Meta:
        model = models.Event
        exclude = ['owner']
