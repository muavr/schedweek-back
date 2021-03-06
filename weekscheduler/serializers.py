from weekscheduler import models
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueTogetherValidator


class EventHyperLinkedSerializer(serializers.HyperlinkedModelSerializer):
    created_ts = serializers.ReadOnlyField()
    modified_ts = serializers.ReadOnlyField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        # validate time interval
        start_time = attrs.get('start_time')
        if start_time is None and self.instance:
            start_time = self.instance.start_time

        finish_time = attrs.get('finish_time')
        if finish_time is None and self.instance:
            finish_time = self.instance.finish_time

        if start_time >= finish_time:
            raise serializers.ValidationError(_('Starting time of event must be lesser than its finish time.'))
        return attrs

    class Meta:
        model = models.Event
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=models.Event.objects.all(),
                fields=('owner', 'day_of_week', 'start_time', 'title',)
            )
        ]
