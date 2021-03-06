import json

from weekscheduler.models import Event
from weekscheduler.serializers import EventHyperLinkedSerializer

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase, APIRequestFactory


class EventAPITestCase(APITestCase):

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

    @staticmethod
    def get_serialized_event(event):
        factory = APIRequestFactory()
        fake_request = factory.get('/')
        return JSONRenderer().render(
            EventHyperLinkedSerializer(instance=event, context={'request': fake_request}).data)


class EventCreateAPIViewTestCase(EventAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("event-list")

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

        self.api_authentication()
        response = self.client.get(self.url)
        self.assertEqual(len(json.loads(response.content)), Event.objects.filter(owner=self.user).count())


class EventDetailAPIViewTestCase(EventAPITestCase):

    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(**{
            'title': 'Important Boris\'s task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:00',
            'finish_time': '10:15'
        }, owner=self.user)
        self.url = reverse('event-detail', kwargs={'pk': self.event.pk})

    def test_retrieve_event(self):
        serializer_event_data = self.get_serialized_event(self.event)

        response = self.client.get(self.url)
        response_event_data = response.content
        self.assertEqual(serializer_event_data, response_event_data)

    def test_unauthorized_calls_by_other_user(self):
        hacker = User.objects.create_user(username='hacker', password='password')
        hacker_token = RefreshToken.for_user(hacker).access_token
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + str(hacker_token))

        # HTTP GET
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

        # HTTP PUT
        response = self.client.put(self.url, {
            'title': 'Important Boris\'s task',
            'description': 'Some informative description',
            'day_of_week': 0,
            'start_time': '10:00',
            'finish_time': '10:30'
        })
        self.assertEqual(403, response.status_code)

        # HTTP PATCH
        response = self.client.patch(self.url, {'finish_time': '10:30'})
        self.assertEqual(403, response.status_code)

        # HTTP DELETE
        response = self.client.delete(self.url)
        self.assertEqual(403, response.status_code)

    def test_update_event(self):
        response = self.client.put(self.url, {
            'title': 'Not important Boris\'s task',
            'description': 'Some none-informative description',
            'day_of_week': 1,
            'start_time': '10:10',
            'finish_time': '10:30'
        })
        response_event_data = response.content

        event = Event.objects.get(pk=self.event.id)
        serializer_event_data = self.get_serialized_event(event)

        self.assertEqual(response_event_data, serializer_event_data)
        self.assertEqual(200, response.status_code)

    def test_partial_update_event(self):
        response = self.client.patch(self.url, {
            'finish_time': '10:30'
        })
        response_event_data = response.content

        event = Event.objects.get(pk=self.event.id)
        serializer_event_data = self.get_serialized_event(event)

        self.assertEqual(response_event_data, serializer_event_data)
        self.assertEqual(200, response.status_code)

    def test_partial_update_event_in_case_wrong_time_interval(self):
        response = self.client.patch(self.url, {
            'start_time': '10:16'
        })
        self.assertEqual(400, response.status_code)

        response = self.client.patch(self.url, {
            'finish_time': '9:00'
        })
        self.assertEqual(400, response.status_code)

    def test_remove_event(self):
        response = self.client.delete(self.url)
        event = Event.objects.filter(pk=self.event.id)
        self.assertEqual(0, len(event))
        self.assertEqual(204, response.status_code)
