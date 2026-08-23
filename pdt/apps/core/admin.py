from django.contrib import admin

from .admin_mixins import SeedLockingAdminMixin
from .models import GlossaryTerm


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(SeedLockingAdminMixin, admin.ModelAdmin):
    list_display = ("term", "definition", "seed_managed")
    list_filter = ("seed_managed",)
    search_fields = ("term", "definition")
    ordering = ("term",)
