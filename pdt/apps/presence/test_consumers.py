"""Testes assíncronos dos consumers WebSocket (presence + sala de ajuda)."""
from __future__ import annotations

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model

from apps.courses.models import Phase, Topic
from apps.presence.help_consumer import HelpRoomConsumer
from apps.presence.models import HelpChatMessage, HelpRequest

User = get_user_model()


@database_sync_to_async
def _make_user(**kwargs):
    defaults = {
        "email": "wsuser@example.com",
        "password": "test-pass-1234",
        "admission_passed": True,
        "full_name": "WS User",
    }
    defaults.update(kwargs)
    pwd = defaults.pop("password")
    return User.objects.create_user(password=pwd, **defaults)


@database_sync_to_async
def _make_help_request(requester, helper=None, status=HelpRequest.JOINED):
    phase, _ = Phase.objects.get_or_create(name="Fase WS", defaults={"order": 1})
    topic, _ = Topic.objects.get_or_create(
        phase=phase, order=1, defaults={"title": "Tópico WS"}
    )
    return HelpRequest.objects.create(
        requester=requester, helper=helper, topic=topic, status=status
    )


def _make_communicator(help_id, user):
    """Constrói um WebsocketCommunicator com user já injetado no scope."""
    communicator = WebsocketCommunicator(
        HelpRoomConsumer.as_asgi(),
        f"/ws/help/{help_id}/",
    )
    communicator.scope["user"] = user
    communicator.scope["url_route"] = {"kwargs": {"help_id": str(help_id)}}
    return communicator


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestHelpRoomConsumer:
    async def test_anonimo_e_rejeitado(self):
        from django.contrib.auth.models import AnonymousUser

        hr = await _make_help_request(
            requester=await _make_user(email="r1@x.com")
        )
        communicator = _make_communicator(hr.id, AnonymousUser())
        connected, _ = await communicator.connect()
        assert connected is False

    async def test_estranho_e_rejeitado(self):
        requester = await _make_user(email="r2@x.com")
        helper = await _make_user(email="h2@x.com")
        estranho = await _make_user(email="e2@x.com")
        hr = await _make_help_request(requester=requester, helper=helper)

        communicator = _make_communicator(hr.id, estranho)
        connected, _ = await communicator.connect()
        assert connected is False

    async def test_requester_consegue_se_conectar(self):
        requester = await _make_user(email="r3@x.com")
        hr = await _make_help_request(requester=requester, status=HelpRequest.OPEN)
        communicator = _make_communicator(hr.id, requester)
        connected, _ = await communicator.connect()
        assert connected is True
        # Recebe mensagem "joined"
        msg = await communicator.receive_json_from()
        assert msg["type"] == "system"
        assert msg["kind"] == "joined"
        await communicator.disconnect()

    async def test_chat_propaga_para_o_outro_usuario(self):
        requester = await _make_user(email="r4@x.com", full_name="Requester")
        helper = await _make_user(email="h4@x.com", full_name="Helper")
        hr = await _make_help_request(requester=requester, helper=helper)

        c_req = _make_communicator(hr.id, requester)
        c_help = _make_communicator(hr.id, helper)
        ok1, _ = await c_req.connect()
        ok2, _ = await c_help.connect()
        assert ok1 and ok2

        # drena mensagens system iniciais
        await c_req.receive_json_from()
        await c_req.receive_json_from()
        await c_help.receive_json_from()

        await c_req.send_json_to({"action": "chat", "text": "olá!"})

        msg_req = await c_req.receive_json_from()
        msg_help = await c_help.receive_json_from()
        assert msg_req["type"] == "chat"
        assert msg_req["text"] == "olá!"
        assert msg_req["self"] is True
        assert msg_help["type"] == "chat"
        assert msg_help["text"] == "olá!"
        assert msg_help["self"] is False

        saved = await database_sync_to_async(
            lambda: HelpChatMessage.objects.filter(help_request_id=hr.id).count()
        )()
        assert saved == 1

        await c_req.disconnect()
        await c_help.disconnect()

    async def test_chat_vazio_e_ignorado(self):
        requester = await _make_user(email="r5@x.com")
        hr = await _make_help_request(requester=requester, status=HelpRequest.OPEN)
        communicator = _make_communicator(hr.id, requester)
        await communicator.connect()
        await communicator.receive_json_from()  # joined

        await communicator.send_json_to({"action": "chat", "text": "   "})
        # Nenhuma mensagem deve voltar (timeout esperado)
        assert await communicator.receive_nothing(timeout=0.5)
        await communicator.disconnect()

    async def test_signal_eh_relayed_apenas_para_o_outro(self):
        requester = await _make_user(email="r6@x.com")
        helper = await _make_user(email="h6@x.com")
        hr = await _make_help_request(requester=requester, helper=helper)

        c_req = _make_communicator(hr.id, requester)
        c_help = _make_communicator(hr.id, helper)
        await c_req.connect()
        await c_help.connect()
        await c_req.receive_json_from()
        await c_req.receive_json_from()
        await c_help.receive_json_from()

        offer = {"sdp": "v=0...", "type": "offer"}
        await c_req.send_json_to({"action": "signal", "payload": offer})

        # O remetente NÃO deve receber o sinal (o consumer filtra)
        # já o helper recebe.
        msg = await c_help.receive_json_from()
        assert msg["type"] == "signal"
        assert msg["payload"] == offer
        assert msg["from_user_id"] == requester.id
        assert await c_req.receive_nothing(timeout=0.3)

        await c_req.disconnect()
        await c_help.disconnect()

    async def test_help_resolvida_recusa_conexao(self):
        requester = await _make_user(email="r7@x.com")
        hr = await _make_help_request(
            requester=requester, status=HelpRequest.RESOLVED
        )
        communicator = _make_communicator(hr.id, requester)
        connected, _ = await communicator.connect()
        assert connected is False
