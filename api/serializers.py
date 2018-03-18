from rest_framework import serializers

from events.models import EventPage, EventSignup


class UserSerializer(serializers.Serializer):
    discord_user = serializers.CharField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class EventSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSignup
        fields = ('event', 'member', 'signup_created', 'comment')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPage
        fields = (
            'title', 'id', 'location', 'start', 'finish', 'description', 'cancelled', 'signup_limit', 'signup_open',
            'signup_close', 'signup_freshers_open', 'signup_count')
