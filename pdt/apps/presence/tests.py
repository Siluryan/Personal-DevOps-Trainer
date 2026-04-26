"""Testes do app presence: HTTP API de mapa/ajuda e ciclo de vida do HelpRequest."""
from __future__ import annotations

import pytest
from django.urls import reverse

from apps.courses.models import Phase, Topic
from apps.gamification.models import TopicScore
from apps.presence.models import HelpRequest, PresenceState


@pytest.fixture
def topic(db):
    phase = Phase.objects.create(name="Fase Teste", order=1)
    return Topic.objects.create(phase=phase, title="Tópico Ajuda", order=1)


@pytest.mark.django_db
class TestPresenceAPIs:
    def test_checkin_atualiza_localizacao(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.post(
            reverse("presence:api_checkin"),
            {"lat": "-23.5", "lng": "-46.6"},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

        state = PresenceState.objects.get(user=admitted_user)
        assert state.latitude == -23.5
        assert state.longitude == -46.6
        assert state.status == PresenceState.AVAILABLE

    def test_checkin_lat_lng_invalidos_retorna_400(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.post(
            reverse("presence:api_checkin"),
            {"lat": "not-a-float", "lng": "0"},
        )
        assert resp.status_code == 400

    def test_checkin_falha_sem_dados(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.post(reverse("presence:api_checkin"), {})
        assert resp.status_code == 400

    def test_online_users_retorna_apenas_disponiveis_no_mapa(
        self, client, admitted_user, make_user
    ):
        client.force_login(admitted_user)
        outro = make_user(email="outro@x.com", show_on_map=True)
        offline = make_user(email="offline@x.com", show_on_map=True)

        PresenceState.objects.create(
            user=admitted_user,
            latitude=1.0,
            longitude=1.0,
            status=PresenceState.AVAILABLE,
        )
        PresenceState.objects.create(
            user=outro,
            latitude=2.0,
            longitude=2.0,
            status=PresenceState.HELP,
        )
        PresenceState.objects.create(
            user=offline,
            latitude=3.0,
            longitude=3.0,
            status=PresenceState.OFFLINE,
        )

        resp = client.get(reverse("presence:api_online"))
        users = resp.json()["users"]
        names = {u["name"] for u in users}
        assert admitted_user.display_name in names
        assert outro.display_name in names
        assert offline.display_name not in names


@pytest.mark.django_db
class TestHelpRequestAPI:
    def test_pedido_de_ajuda_marca_status_help(self, client, admitted_user, topic):
        client.force_login(admitted_user)
        resp = client.post(
            reverse("presence:api_help_request"),
            {"topic_id": topic.id, "description": "Não entendi a aula"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["topic"] == topic.title

        hr = HelpRequest.objects.get(id=data["id"])
        assert hr.requester == admitted_user
        assert hr.status == HelpRequest.OPEN
        assert hr.room_token

        state = PresenceState.objects.get(user=admitted_user)
        assert state.status == PresenceState.HELP

    def test_novo_pedido_cancela_anterior_aberto(
        self, client, admitted_user, topic
    ):
        client.force_login(admitted_user)
        antigo = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.post(
            reverse("presence:api_help_request"),
            {"topic_id": topic.id, "description": ""},
        )
        antigo.refresh_from_db()
        assert antigo.status == HelpRequest.CANCELLED
        assert HelpRequest.objects.filter(
            requester=admitted_user, status=HelpRequest.OPEN
        ).count() == 1

    def test_pedido_ajuda_negado_sem_aparecer_no_mapa(
        self, client, make_user, topic
    ):
        user = make_user(email="sem-mapa@example.com", show_on_map=False)
        client.force_login(user)
        resp = client.post(
            reverse("presence:api_help_request"),
            {"topic_id": topic.id, "description": "dúvida"},
        )
        assert resp.status_code == 403
        assert "mapa" in resp.json()["error"].lower()
        assert not HelpRequest.objects.filter(requester=user).exists()

    def test_join_help_request(self, client, admitted_user, make_user, topic):
        helper = make_user(email="helper@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(helper)
        resp = client.post(reverse("presence:api_help_join", args=[hr.id]))
        assert resp.status_code == 200
        hr.refresh_from_db()
        assert hr.status == HelpRequest.JOINED
        assert hr.helper == helper

    def test_proprio_requester_nao_pode_dar_join(
        self, client, admitted_user, topic
    ):
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(admitted_user)
        resp = client.post(reverse("presence:api_help_join", args=[hr.id]))
        assert resp.status_code == 400

    def test_join_so_aceita_status_open(self, client, admitted_user, make_user, topic):
        helper = make_user(email="helper@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user,
            topic=topic,
            status=HelpRequest.RESOLVED,
        )
        client.force_login(helper)
        resp = client.post(reverse("presence:api_help_join", args=[hr.id]))
        assert resp.status_code == 400

    def test_resolve_aplica_help_bonus(
        self, client, admitted_user, make_user, topic
    ):
        helper = make_user(email="helper@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user,
            topic=topic,
            helper=helper,
            status=HelpRequest.JOINED,
        )

        client.force_login(admitted_user)
        resp = client.post(reverse("presence:api_help_resolve", args=[hr.id]))
        assert resp.status_code == 200
        hr.refresh_from_db()
        assert hr.status == HelpRequest.RESOLVED
        assert hr.resolved_at is not None

        bonus = TopicScore.objects.get(user=helper, topic=topic)
        assert bonus.help_bonus == 1

    def test_resolve_so_pelo_proprio_requester(
        self, client, admitted_user, make_user, topic
    ):
        outro = make_user(email="outro@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user,
            topic=topic,
            helper=outro,
            status=HelpRequest.JOINED,
        )
        client.force_login(outro)
        resp = client.post(reverse("presence:api_help_resolve", args=[hr.id]))
        assert resp.status_code == 404

    def test_cancel_request(self, client, admitted_user, topic):
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(admitted_user)
        resp = client.post(reverse("presence:api_help_cancel", args=[hr.id]))
        assert resp.status_code == 200
        hr.refresh_from_db()
        assert hr.status == HelpRequest.CANCELLED


@pytest.mark.django_db
class TestHelpRoomView:
    def test_room_visivel_para_requester(self, client, admitted_user, topic):
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(admitted_user)
        resp = client.get(reverse("presence:help_room", args=[hr.id]))
        assert resp.status_code == 200
        assert resp.context["forbidden"] is False

    def test_room_visivel_para_helper(
        self, client, admitted_user, make_user, topic
    ):
        helper = make_user(email="h@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user,
            topic=topic,
            helper=helper,
            status=HelpRequest.JOINED,
        )
        client.force_login(helper)
        resp = client.get(reverse("presence:help_room", args=[hr.id]))
        assert resp.status_code == 200
        assert resp.context["forbidden"] is False

    def test_room_marcada_forbidden_para_estranho(
        self, client, admitted_user, make_user, topic
    ):
        estranho = make_user(email="bisbilhoteiro@x.com")
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(estranho)
        resp = client.get(reverse("presence:help_room", args=[hr.id]))
        assert resp.status_code == 200
        assert resp.context["forbidden"] is True

    def test_room_envia_ice_servers(self, client, admitted_user, topic):
        hr = HelpRequest.objects.create(
            requester=admitted_user, topic=topic, status=HelpRequest.OPEN
        )
        client.force_login(admitted_user)
        resp = client.get(reverse("presence:help_room", args=[hr.id]))
        assert "ice_servers" in resp.context
        assert isinstance(resp.context["ice_servers"], list)


@pytest.mark.django_db
class TestMapView:
    def test_map_view_requer_login(self, client):
        resp = client.get(reverse("presence:map"))
        assert resp.status_code == 302

    def test_map_view_lista_topicos(self, client, admitted_user, topic):
        client.force_login(admitted_user)
        resp = client.get(reverse("presence:map"))
        assert resp.status_code == 200
        assert topic.title.encode() in resp.content

    def test_map_view_sem_mapa_mostra_link_perfil(self, client, make_user, topic):
        u = make_user(email="mapa-off@example.com", show_on_map=False)
        client.force_login(u)
        resp = client.get(reverse("presence:map"))
        assert resp.status_code == 200
        assert reverse("accounts:profile_edit").encode() in resp.content
        assert b"Pedir ajuda exige aparecer no mapa" in resp.content
