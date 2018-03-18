from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.models import CompsocUser
from .serializers import UserSerializer


class MemberDiscordInfoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uni_id):
        user = get_object_or_404(get_user_model(), username=uni_id)
        compsoc_user = CompsocUser.objects.get(user_id=user.id)
        serializer = UserSerializer(compsoc_user)

        return JsonResponse(serializer.data)
