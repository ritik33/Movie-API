from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username", "is_admin", "is_verified")
    list_filter = ("is_admin",)
    fieldsets = (
        (
            "User Credentials",
            {"fields": ("email", "password", "username", "is_verified")},
        ),
        ("Personal info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    search_fields = ("email", "username")
    ordering = ("id", "email")
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
