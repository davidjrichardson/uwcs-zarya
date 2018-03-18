from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import TokenHasScope
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK

from accounts.models import CompsocUser
from events.models import EventPage, EventSignup
from .serializers import UserSerializer, EventSerializer, EventSignupSerializer


class MemberDiscordInfoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uni_id):
        user = get_object_or_404(get_user_model(), username=uni_id)
        compsoc_user = CompsocUser.objects.get(user_id=user.id)
        serializer = UserSerializer(compsoc_user)

        return JsonResponse(serializer.data)


class EventSignupView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['event']

    def post(self, request):
        if not request.data.get('event_id'):
            return JsonResponse({'detail': 'event_id field is required but wasn\'t found'}, status=HTTP_400_BAD_REQUEST)

        data = {
            'event': request.data.get('event_id'),
            'member': request.user.id,
            'comment': request.data.get('comment')
        }

        serialiser = EventSignupSerializer(data=data)
        if serialiser.is_valid():
            serialiser.save()
        else:
            return JsonResponse(serialiser.errors, status=HTTP_400_BAD_REQUEST)

        return JsonResponse(serialiser.data, status=HTTP_201_CREATED)


class EventDeregisterView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['event']

    def get(self, request, event_id):
        signup = get_object_or_404(EventSignup, event=event_id, member=request.user.id)
        signup.delete()

        return JsonResponse({'detail': 'signup deleted'}, status=HTTP_200_OK)


class EventListView(ListAPIView):
    queryset = EventPage.objects.live().filter(finish__gte=timezone.now()).order_by('start')
    serializer_class = EventSerializer
