from django.contrib.auth.models import User
from rest_framework import serializers

from events.models import EventPage, EventSignup, SeatingRoom, SeatingRevision, Seating


class DiscordUserSerialiser(serializers.Serializer):
    discord_user = serializers.CharField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class LanAppProfileSerialiser(serializers.Serializer):
    nickname = serializers.CharField(read_only=True)
    user = UserSerialiser()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SeatingRoomSerialiser(serializers.ModelSerializer):
    class Meta:
        model = SeatingRoom
        fields = ('name', 'tables', 'max_capacity')


class SeatingRevisionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = SeatingRevision
        fields = ('event', 'creator', 'number', 'created_at')


class SeatingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Seating
        fields = ('reserved', 'revision', 'user', 'table', 'seat')


class EventSignupSerialiser(serializers.ModelSerializer):
    class Meta:
        model = EventSignup
        fields = ('event', 'member', 'signup_created', 'comment')


class EventSerialiser(serializers.ModelSerializer):
    class Meta:
        model = EventPage
        fields = (
            'title', 'id', 'location', 'start', 'finish', 'description', 'cancelled', 'signup_limit', 'signup_open',
            'signup_close', 'signup_freshers_open', 'signup_count')
