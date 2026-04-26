"""Lógica compartilhada de presença (logout, broadcast)."""
from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from .consumers import PRESENCE_GROUP
from .models import PresenceState


def broadcast_presence_refresh() -> None:
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(PRESENCE_GROUP, {"type": "presence.refresh"})


def broadcast_presence_refresh_after_commit() -> None:
    transaction.on_commit(broadcast_presence_refresh)


def user_presence_mark_offline(user) -> bool:
    """Marca o usuário como offline no mapa. Retorna True se houve mudança."""
    if not user or not getattr(user, "pk", None):
        return False
    with transaction.atomic():
        state, _ = PresenceState.objects.get_or_create(user=user)
        if state.status == PresenceState.OFFLINE:
            return False
        state.status = PresenceState.OFFLINE
        state.save(update_fields=["status", "last_seen"])
        broadcast_presence_refresh_after_commit()
    return True
