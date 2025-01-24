from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class DynamicDataSerializer(serializers.Serializer):
    some_field = serializers.CharField(max_length=100)
