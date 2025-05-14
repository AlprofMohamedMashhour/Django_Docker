from django.urls import path
from .views import *




urlpatterns = [

#     ***********************************
    # Groups
    path('get_groups/',get_groups),

    path('get_profile/', get_profile),   
    path('edit_profile/', edit_profile), 
    path('change_password/', change_password),  

    path('AdminOp/add/', AdminOp.as_view()),
    path('AdminOp/edit/<int:pk>/', AdminOp.as_view()),
    path('AdminOp/delete/<int:pk>/', AdminOp.as_view()),
    path('GetAdminById/<int:pk>/', AdminOp.as_view()),
    path('AdminList/', AdminList.as_view()),
    path('GetAdminList/', AdminList.as_view()),

    path('EmployeeOp/add/', EmployeeOp.as_view()),
    path('EmployeeOp/edit/<int:pk>/', EmployeeOp.as_view()),
    path('EmployeeOp/delete/<int:pk>/', EmployeeOp.as_view()),
    path('GetEmployeeById/<int:pk>/', EmployeeOp.as_view()),
    path('EmployeeList/', EmployeeList.as_view()),
    path('GetEmployeeList/', EmployeeList.as_view()),
    

]
