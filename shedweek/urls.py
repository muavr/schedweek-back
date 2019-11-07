from django.contrib import admin
from django.conf import settings
from weekscheduler import views
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('events', views.EventViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.extend([
        path('api-auth/', include('rest_framework.urls'))
    ])

