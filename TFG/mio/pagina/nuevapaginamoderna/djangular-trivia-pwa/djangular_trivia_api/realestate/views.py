from django.core import serializers
from django.http import JsonResponse
from django.views import View

from .ice_interface import retrieve_properties, retrieve_zones
from .models import Property, Zone


class PropertyListView(View):
    def get(self, request):
        properties = retrieve_properties()
        properties_json = serializers.serialize('json', properties)
        return JsonResponse(properties_json, safe=False)


class ZoneListView(View):
    def get(self, request):
        zones = retrieve_zones()
        zones_json = serializers.serialize('json', zones)
        return JsonResponse(zones_json, safe=False)
