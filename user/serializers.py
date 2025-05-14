from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from django.contrib.auth.models import Group


#*****************************************
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)


    def validate(self, data):
        # Validate old password
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Current password is incorrect"})
        return data

    def update(self, instance, validated_data):
        # Update password
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class AdminCreateSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Admin
        fields = ['id', 'username', 'phone_number', 'password', 'groups','is_active' ]
    
    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        admin = super().create(validated_data)
        if groups:
            admin.groups.set(groups)
        return admin

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        
        admin = super().update(instance, validated_data)
        groups = validated_data.pop('groups', None)

        if groups:
            admin.groups.set(groups)
            return admin
        return admin

class AdminViewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = Admin
        fields = ['id', 'username', 'phone_number','groups', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Employee
        fields = ['id', 'username', 'phone_number', 'password', 'groups','is_active' ]
    
    def create(self, validated_data):
        # Extract groups if provided
        groups = validated_data.pop('groups', [])
        # Create the employee
        employee = super().create(validated_data)
        # Add groups if provided
        if groups:
            employee.groups.set(groups)
        return employee

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        
        employee = super().update(instance, validated_data)
        # Extract groups if provided
        groups = validated_data.pop('groups', None)
        # Update the employee

        # Update groups if provided
        if groups:
            employee.groups.set(groups)
            return employee
        return employee

class EmployeeViewSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = Employee
        fields = [ 'id', 'username', 'phone_number','groups', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


#*****************************************
