from weekscheduler import models
from weekscheduler import serializers
from rest_framework.viewsets import ModelViewSet


class EventViewSet(ModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventHyperLinkedSerializer

