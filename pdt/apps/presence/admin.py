from django.contrib import admin

from .models import HelpRequest, PresenceState


@admin.register(PresenceState)
class PresenceStateAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "latitude", "longitude", "last_seen")
    list_filter = ("status",)
    search_fields = ("user__email",)


@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ("requester", "topic", "status", "helper", "created_at", "resolved_at")
    list_filter = ("status", "topic__phase")
    search_fields = ("requester__email", "helper__email", "topic__title")
