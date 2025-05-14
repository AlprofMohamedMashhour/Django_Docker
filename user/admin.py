from django.contrib import admin
from .models import *
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','username')
admin.site.register(CustomUser,CustomUserAdmin)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('id','username','is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('username',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)
    
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','username','is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('username',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


