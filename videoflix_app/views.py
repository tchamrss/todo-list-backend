from django.shortcuts import render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from videoflix_app.serializers import VideoSerializer
from videoflix_app.models import Video
from rest_framework import authentication, permissions
from rest_framework.response import Response


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.
#@cache_page(CACHE_TTL)

""" from videoflix_app.admin import VideoResource
dataset = VideoResource().export()
dataset.json """

class VideoView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all todos.
        """
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)