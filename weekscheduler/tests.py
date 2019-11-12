import json
from weekscheduler.models import Event
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class EventCreateAPIViewTestCase(APITestCase):
    url = reverse("event-list")

    def setUp(self):
        self.username = 'Boris'
        self.email = 'boris.email@example.com'
        self.password = 'boris_password'
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.refresh = RefreshToken.for_user(self.user)
        self.token = self.refresh.access_token
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(self.token))

    def test_create_valid_event(self):
        response = self.client.post(self.url, {
            'title': 'Important task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:00',
            'finish_time': '10:15'
        })
        self.assertEqual(201, response.status_code)

    def test_create_event_with_wrong_day_of_week(self):
        # day_of_week field must equal from 0 to 6
        response = self.client.post(self.url, {
            'title': 'Important task',
            'description': 'Some informative description',
            'day_of_week': 7,
            'start_time': '15:10',
            'finish_time': '15:00'
        })
        self.assertEqual(400, response.status_code)

    def test_create_event_with_wrong_time_interval(self):
        # Start time must be lesser than finish time
        response = self.client.post(self.url, {
            'title': 'Important task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '15:10',
            'finish_time': '15:00'
        })
        self.assertEqual(400, response.status_code)

    def test_create_event_with_same_start_finish_time(self):
        # Start time must be strictly lesser than finish time
        response = self.client.post(self.url, {
            'title': 'Important task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '15:00',
            'finish_time': '15:00'
        })
        self.assertEqual(400, response.status_code)

    def test_create_user_bound_event(self):
        self.client.post(self.url, {
            'title': 'Important Boris\'s task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:00',
            'finish_time': '10:15'
        })
        self.client.post(self.url, {
            'title': 'Important Boris\'s task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:15',
            'finish_time': '10:30'
        })

        username = 'Ivan'
        email = 'ivan.email@example.com'
        password = 'ivan_password'
        another_user = User.objects.create_user(username, email, password)
        refresh = RefreshToken.for_user(another_user)
        token = refresh.access_token
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(token))

        self.client.post(self.url, {
            'title': 'Important Ivan\'s task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:00',
            'finish_time': '10:15'
        })

        response = self.client.get(self.url)
        self.assertEqual(len(json.loads(response.content)), Event.objects.filter(owner=another_user).count())
