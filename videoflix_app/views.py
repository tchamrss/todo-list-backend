from django.shortcuts import render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.
#@cache_page(CACHE_TTL)

""" from videoflix_app.admin import VideoResource
dataset = VideoResource().export()
dataset.json """