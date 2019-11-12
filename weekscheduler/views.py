from weekscheduler import models
from weekscheduler import serializers
from rest_framework.viewsets import ModelViewSet


class EventViewSet(ModelViewSet):
    queryset = models.Event.objects.none()
    serializer_class = serializers.EventHyperLinkedSerializer

    def get_queryset(self):
        user = self.request.user
        if user:
            return models.Event.objects.filter(owner=user)
        return models.Event.objects.none()

