from django.urls import path
from weekscheduler.views import EventListView, EventDetailView

urlpatterns = [
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<int:pk>', EventDetailView.as_view(), name='event-detail'),
]
