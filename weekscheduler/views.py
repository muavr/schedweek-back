from weekscheduler import models
from weekscheduler import serializers
from weekscheduler.permissions import IsEventOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class EventListView(ListCreateAPIView):
    serializer_class = serializers.EventHyperLinkedSerializer

    def get_queryset(self):
        user = self.request.user
        if user:
            return models.Event.objects.filter(owner=user)
        return models.Event.objects.none()


class EventDetailView(RetrieveUpdateDestroyAPIView):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventHyperLinkedSerializer
    permission_classes = (IsAuthenticated, IsEventOwner)


