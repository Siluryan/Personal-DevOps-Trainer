"""Consumer da sala de ajuda, chat + sinalização WebRTC (voz).

Trafega no grupo `help-<id>`. Apenas o `requester` e o `helper` daquele
HelpRequest podem se conectar; qualquer outro usuário é desconectado.

Mensagens trocadas (action):
  - chat        : `{action: "chat", text: "..."}`
  - signal      : `{action: "signal", payload: {...}}`  # offer/answer/ICE
  - typing      : `{action: "typing"}`
  - leave       : `{action: "leave"}`

Eventos enviados ao cliente (type):
  - chat        : mensagem textual de outro usuário (ou eco do próprio)
  - signal      : payload WebRTC (offer/answer/ICE) destinado ao peer
  - presence    : quem está na sala agora (lista de display_names)
  - system      : avisos do servidor (entrada, saída, resolução)
"""
from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


def help_group_name(help_request_id: int) -> str:
    return f"help-{help_request_id}"


class HelpRoomConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket de uma sala de ajuda específica."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        try:
            self.help_id = int(self.scope["url_route"]["kwargs"]["help_id"])
        except (KeyError, ValueError):
            await self.close(code=4400)
            return

        help_request = await self._fetch_help_request(self.help_id)
        if not help_request:
            await self.close(code=4404)
            return

        if user.id not in (help_request["requester_id"], help_request["helper_id"]):
            await self.close(code=4403)
            return

        if help_request["status"] in ("resolved", "cancelled"):
            await self.close(code=4410)
            return

        self.user = user
        self.display_name = getattr(user, "display_name", user.get_username())
        self.group = help_group_name(self.help_id)

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.group,
            {
                "type": "help.system",
                "kind": "joined",
                "user_id": user.id,
                "name": self.display_name,
                "ts": timezone.now().isoformat(),
            },
        )

    async def disconnect(self, code):
        if not getattr(self, "group", None):
            return
        try:
            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "help.system",
                    "kind": "left",
                    "user_id": getattr(self.user, "id", None),
                    "name": getattr(self, "display_name", ""),
                    "ts": timezone.now().isoformat(),
                },
            )
            await self.channel_layer.group_discard(self.group, self.channel_name)
        except Exception:  # noqa: BLE001
            pass

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action == "chat":
            text = (content.get("text") or "").strip()
            if not text:
                return
            text = text[:2000]
            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "help.chat",
                    "user_id": self.user.id,
                    "name": self.display_name,
                    "text": text,
                    "ts": timezone.now().isoformat(),
                },
            )
        elif action == "signal":
            payload = content.get("payload")
            if payload is None:
                return
            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "help.signal",
                    "from_user_id": self.user.id,
                    "from_name": self.display_name,
                    "payload": payload,
                },
            )
        elif action == "typing":
            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "help.typing",
                    "user_id": self.user.id,
                    "name": self.display_name,
                },
            )

    async def help_chat(self, event):
        await self.send_json(
            {
                "type": "chat",
                "user_id": event["user_id"],
                "name": event["name"],
                "text": event["text"],
                "ts": event["ts"],
                "self": event["user_id"] == self.user.id,
            }
        )

    async def help_signal(self, event):
        if event["from_user_id"] == self.user.id:
            return
        await self.send_json(
            {
                "type": "signal",
                "from_user_id": event["from_user_id"],
                "from_name": event["from_name"],
                "payload": event["payload"],
            }
        )

    async def help_system(self, event):
        await self.send_json(
            {
                "type": "system",
                "kind": event["kind"],
                "user_id": event.get("user_id"),
                "name": event.get("name"),
                "ts": event.get("ts"),
                "self": event.get("user_id") == self.user.id,
            }
        )

    async def help_typing(self, event):
        if event["user_id"] == self.user.id:
            return
        await self.send_json(
            {"type": "typing", "user_id": event["user_id"], "name": event["name"]}
        )

    @database_sync_to_async
    def _fetch_help_request(self, pk: int):
        from .models import HelpRequest
        try:
            hr = HelpRequest.objects.get(pk=pk)
        except HelpRequest.DoesNotExist:
            return None
        return {
            "requester_id": hr.requester_id,
            "helper_id": hr.helper_id,
            "status": hr.status,
        }
