"""Payload JSON único para o mapa: HTTP `/api/online/` e WebSocket `presence`."""
from __future__ import annotations

from .models import HelpRequest, PresenceState


def build_online_users_payload() -> list[dict]:
    rows = (
        PresenceState.objects.select_related("user")
        .exclude(status=PresenceState.OFFLINE)
        .filter(user__show_on_map=True, latitude__isnull=False, longitude__isnull=False)
    )
    active_help: dict[int, HelpRequest] = {}
    for h in (
        HelpRequest.objects.filter(status__in=[HelpRequest.OPEN, HelpRequest.JOINED])
        .select_related("topic")
        .order_by("-id")
    ):
        active_help.setdefault(h.requester_id, h)

    payload: list[dict] = []
    for p in rows:
        help_req = active_help.get(p.user_id)
        payload.append(
            {
                "user_id": p.user_id,
                "name": p.user.display_name,
                "lat": p.latitude,
                "lng": p.longitude,
                "status": p.status,
                "help_request_id": help_req.id if help_req else None,
                "help_request_status": help_req.status if help_req else None,
                "help_topic": help_req.topic.title if help_req else None,
            }
        )
    return payload
