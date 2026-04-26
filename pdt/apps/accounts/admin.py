from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "full_name",
        "admission_passed",
        "admission_score",
        "show_in_leaderboard",
        "is_staff",
    )
    search_fields = ("email", "full_name", "linkedin_url", "github_url")
    list_filter = ("admission_passed", "show_in_leaderboard", "is_staff", "is_superuser")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Perfil",
            {
                "fields": (
                    "full_name",
                    "country",
                    "bio",
                    "linkedin_url",
                    "github_url",
                )
            },
        ),
        (
            "Plataforma",
            {
                "fields": (
                    "admission_passed",
                    "admission_score",
                    "show_in_leaderboard",
                    "show_on_map",
                )
            },
        ),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
