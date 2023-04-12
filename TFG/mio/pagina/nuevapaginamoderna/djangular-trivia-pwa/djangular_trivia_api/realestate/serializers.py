# serializers.py
from rest_framework import serializers

from .models import Property, Zone


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'
