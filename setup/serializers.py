
from rest_framework import serializers
from .models import *


# class TestSerializer(serializers.ModelSerializer):
#     lab = serializers.CharField(source='lab.name', read_only=True)
#     class Meta:
#         model = Test
#         fields = ['id','lab','name', 'code', 'is_active', 'is_deleted']

