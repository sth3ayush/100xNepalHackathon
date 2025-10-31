from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'mobile_no', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'mobile_no')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'mobile_no', 'profile_picture', 'points')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'mobile_no', 
                'profile_picture', 'points', 'password1', 'password2', 
                'is_staff', 'is_active'
            )}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmergencyEmail)
admin.site.register(Memory)
admin.site.register(MemoryMedia)
admin.site.register(GuideProfile)