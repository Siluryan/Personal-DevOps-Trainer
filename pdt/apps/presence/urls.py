from django.urls import path

from . import views

app_name = "presence"

urlpatterns = [
    path("", views.MapView.as_view(), name="map"),
    path("api/online/", views.online_users, name="api_online"),
    path("api/presence/offline/", views.presence_offline, name="api_presence_offline"),
    path("api/help/active-room/", views.active_help_room, name="api_help_active_room"),
    path("api/checkin/", views.checkin, name="api_checkin"),
    path("api/help/request/", views.create_help_request, name="api_help_request"),
    path("api/help/<int:pk>/join/", views.join_help_request, name="api_help_join"),
    path("api/help/<int:pk>/resolve/", views.resolve_help_request, name="api_help_resolve"),
    path("api/help/<int:pk>/cancel/", views.cancel_help_request, name="api_help_cancel"),
    path("ajuda/<int:pk>/", views.HelpRoomView.as_view(), name="help_room"),
]
