"""Consumer WebSocket que mantém o mapa de presença em tempo real."""
from __future__ import annotations

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

PRESENCE_GROUP = "presence-global"


class PresenceConsumer(AsyncJsonWebsocketConsumer):
    """Mantém um grupo global; envia atualizações quando alguém muda de status."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        if not getattr(user, "admission_passed", False):
            await self.close(code=4403)
            return

        self.user = user
        await self.channel_layer.group_add(PRESENCE_GROUP, self.channel_name)
        await self.accept()
        await self._mark_online()
        await self.broadcast_state()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(PRESENCE_GROUP, self.channel_name)
        except Exception:  # noqa: BLE001
            pass
        # Não marcar OFFLINE ao fechar só o WS (troca de página fora do /mapa/).
        # last_seen é renovado pelo ping HTTP em base.html; TTL remove o pin se
        # o navegador fechou ou a sessão encerrou.

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action == "update_location":
            lat = content.get("lat")
            lng = content.get("lng")
            if lat is None or lng is None:
                return
            await self._update_location(float(lat), float(lng))
            await self.broadcast_state()
        elif action == "ping":
            await self.send_json({"type": "pong", "ts": timezone.now().isoformat()})

    async def broadcast_state(self):
        await self.channel_layer.group_send(
            PRESENCE_GROUP, {"type": "presence.refresh"}
        )

    async def presence_refresh(self, event):
        payload = await self._build_payload()
        await self.send_json({"type": "presence", "users": payload})

    @database_sync_to_async
    def _build_payload(self):
        from .online_payload import build_online_users_payload

        return build_online_users_payload()

    @database_sync_to_async
    def _mark_online(self):
        from .models import HelpRequest, PresenceState
        state, _ = PresenceState.objects.get_or_create(user=self.user)
        has_open_help = HelpRequest.objects.filter(
            requester=self.user,
            status__in=[HelpRequest.OPEN, HelpRequest.JOINED],
        ).exists()
        if has_open_help:
            state.status = PresenceState.HELP
        elif state.status == PresenceState.OFFLINE:
            state.status = PresenceState.AVAILABLE
        state.save()
        return state

    @database_sync_to_async
    def _update_location(self, lat: float, lng: float):
        from .models import PresenceState
        state, _ = PresenceState.objects.get_or_create(user=self.user)
        state.latitude = lat
        state.longitude = lng
        if state.status == PresenceState.OFFLINE:
            state.status = PresenceState.AVAILABLE
        state.save()
