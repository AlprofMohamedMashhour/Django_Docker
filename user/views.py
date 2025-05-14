from functools import partial
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import Group
from django.http import Http404

from .serializers import *
from .models import *

import logging
logger = logging.getLogger('project')



#*************************************
class GenralCRUD(APIView):
    model = None
    serializer_class = None
    serializer_class_view = None

    # Configuration for authentication and group permissions
    method_permissions = {
        'post': {
            'auth_required': False,
            'groups': []
        },
        'get': {
            'auth_required': False,
            'groups': []
        },
        'put': {
            'auth_required': False,
            'groups': []
        },
        'delete': {
            'auth_required': False,
            'groups': []
        }
    }

    def check_perm(self, request, method):
        # Get permission configuration for the specific method
        try:
            method_config = self.method_permissions.get(method, {})

        except Exception as e:
            print("erroe: ",e)
            return Response({"data": "Not Found","Exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Check authentication requirement
        if method_config.get('auth_required', False):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication is required for this action")
        
        # If authentication is required or user is authenticated, check group permissions
        if request.user.is_authenticated:
            required_groups = method_config.get('groups', [])
            if required_groups:
                user_groups = request.user.groups.values_list('name', flat=True)
                if not any(group in required_groups for group in user_groups):
                    raise PermissionDenied(f"You do not have permission to perform this action. Required groups: {required_groups}")

    def get_object(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get_serializer_viw(self, *args, **kwargs):
        return self.serializer_class_view(*args, **kwargs)
     
    def post(self, request, format=None):
        # additional_data = {'employee': request.user.id}  # Additional data you want to add
        # request.data.update(additional_data)
        self.check_perm(request, method='post')
        try:

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"data": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            logger.error(f"{self.model} General CRUD Post error: {str(e)}")
            return Response({"data": "Not found","Exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        self.check_perm(request, method='get')
        try:
            instance = self.get_object(pk)
            serializer = self.get_serializer_viw(instance)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"{self.model} General CRUD Get error: {str(e)}")
            return Response({"data": "Not found","Exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
            self.check_perm(request, method='put')
            try:
                
                instance = self.get_object(pk)
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                
                try:
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
                except serializers.ValidationError as ve:
                    # Handle validation errors specifically
                    return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                logger.error(f"{self.model} General CRUD Put error: {str(e)}")
                return Response({"data": "Update failed", "Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        self.check_perm(request, method='delete')
        try:
            instance = self.get_object(pk)
            instance.delete()
            return Response({"data": "Delete successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"{self.model} General CRUD Delete error: {str(e)}")
            return Response({"data": "Delete failed","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GenralList(APIView):
    model = None
    serializer_class = None

    method_permissions = {
        'post': {
            'auth_required': False,
            'groups': []
        },
        'get': {
            'auth_required': False,
            'groups': []
        }
    }

    def filter_objects(self, queryset, search):
        # Check if the search term should be applied
        if search:
            # Retrieve model fields
            model_fields = [f.name for f in self.model._meta.fields]
            
            # Apply filtering based on model fields
            if 'name' in model_fields:
                return queryset.filter(name__icontains=search)
            elif 'first_name' in model_fields:
                return queryset.filter(first_name__icontains=search)
            elif 'is_deleted' in model_fields:
                return queryset.filter(is_deleted=False)
        
        return queryset

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def post(self, request, format=None):
        self.check_perm(request, method='post')
        try:
            page_number = request.data.get('pageNum', 1)
            page_size = request.data.get('pageLen', 10)
            search = request.data.get('search', '')
            data = self.filter_objects(self.model.objects.all(), search)
            paginator = Paginator(data, page_size)
            pages = paginator.get_page(page_number)
            serializer = self.get_serializer(pages, many=True)
            response_data = {
                'count': len(data),
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"{self.model} General List Post error: {str(e)}")
            return Response({"data": "Not Found","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        self.check_perm(request, method='get')
        try:
            data = self.model.objects.filter(is_deleted=False)
            serializer = self.get_serializer(data, many=True)
            # print(serializer.data)
            response_data = {
                'count': data.count(),
                'data': serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"{self.model} General List Get error: {str(e)}")
            return Response({"data": "Not Found","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

#**************************************

#**********************************
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_groups(request):
    try:
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    except Exception as e:
        
        logger.error(f"get Groups error: {str(e)}")
        return Response({"data":"Not Found","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

#***********************************
@api_view(('GET',))
@permission_classes([IsAuthenticated])
def get_profile(request, format=None):
    try:
        user = request.user
        try:
            profile = Employee.objects.get(id=user.id)
            serializer_class = EmployeeViewSerializer
        except Employee.DoesNotExist:
            try:
                profile = Admin.objects.get(id=user.id)
                serializer_class = AdminViewSerializer
            except Admin.DoesNotExist:
                return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)


        serializer = serializer_class(request.user)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        
        logger.error(f"Profile Create error: {str(e)}")
        return Response({"data":"Not Found","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    try:
        user = request.user
        try:
            profile = Employee.objects.get(id=user.id)
            serializer_class = EmployeeCreateSerializer
        except Employee.DoesNotExist:
            try:
                profile = Admin.objects.get(id=user.id)
                serializer_class = AdminCreateSerializer
            except Admin.DoesNotExist:
                return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data},status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    except Exception as e:
        
        logger.error(f"Profile update error: {str(e)}")
        return Response({"error": "An unexpected error occurred during profile update","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response({"data": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        
        logger.error(f"Change Password error: {str(e)}")
        return Response({"error": "An unexpected error occurred during password change","exception":str(e)}, status=status.HTTP_400_BAD_REQUEST)


#***********************************
class AdminOp(GenralCRUD):
    model = Admin
    serializer_class = AdminCreateSerializer
    serializer_class_view=AdminViewSerializer
    method_permissions = {
        'post': {'auth_required': True,'groups': []},
        'get': {'auth_required': True,'groups': []},
        'put': {'auth_required': True,'groups': []},
        'delete': {'auth_required': True,'groups': []}
    }

class AdminList(GenralList):
    model = Admin
    serializer_class = AdminViewSerializer
    method_permissions = {
        'post': {'auth_required': True,'groups': []},
        'get': {'auth_required': True,'groups': []},
    }


#***********************************
class EmployeeOp(GenralCRUD):
    model = Employee
    serializer_class = EmployeeCreateSerializer
    serializer_class_view=EmployeeViewSerializer
    method_permissions = {
        'post': {'auth_required': True,'groups': []},
        'get': {'auth_required': True,'groups': []},
        'put': {'auth_required': True,'groups': []},
        'delete': {'auth_required': True,'groups': []}
    }

class EmployeeList(GenralList):
    model = Employee
    serializer_class = EmployeeViewSerializer
    method_permissions = {
        'post': {'auth_required': True,'groups': []},
        'get': {'auth_required': True,'groups': []},
    }

