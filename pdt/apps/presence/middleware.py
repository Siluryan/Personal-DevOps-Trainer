"""Heartbeat de presença via middleware.

Mantém `last_seen` atualizado em toda navegação autenticada (não só no /mapa),
evitando sumiço indevido do pin quando o frontend não consegue enviar ping.
"""
from __future__ import annotations

from django.utils import timezone

from .models import HelpRequest, PresenceState
from .services import broadcast_presence_refresh_after_commit


class PresenceHeartbeatMiddleware:
    """Atualiza presença em requests autenticadas do usuário aprovado."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user
            and user.is_authenticated
            and getattr(user, "admission_passed", False)
            and not request.path.startswith("/static/")
            and not request.path.startswith("/media/")
        ):
            state, _ = PresenceState.objects.get_or_create(user=user)
            has_open_help = HelpRequest.objects.filter(
                requester=user,
                status__in=[HelpRequest.OPEN, HelpRequest.JOINED],
            ).exists()
            target_status = PresenceState.HELP if has_open_help else PresenceState.AVAILABLE
            if state.status == PresenceState.OFFLINE:
                state.status = target_status
                state.save(update_fields=["status", "last_seen"])
                broadcast_presence_refresh_after_commit()
            else:
                PresenceState.objects.filter(pk=state.pk).update(last_seen=timezone.now())

        return self.get_response(request)

