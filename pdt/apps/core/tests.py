"""Testes do app core: landing, dashboard, doação e context processor."""
from __future__ import annotations

import json

import pytest
from django.core import checks
from django.test import RequestFactory
from django.urls import resolve, reverse

from apps.core.templatetags.pdt_extras import nav_section_active
from apps.courses.models import Phase, Topic
from apps.gamification.models import TopicScore


class TestNavSectionActive:
    def test_trilha_ativa_em_rotas_courses(self):
        req = RequestFactory().get("/trilha/")
        req.resolver_match = resolve("/trilha/")
        assert nav_section_active(req, "courses") is True
        assert nav_section_active(req, "dashboard") is False

    def test_dashboard_ativo(self):
        req = RequestFactory().get("/dashboard/")
        req.resolver_match = resolve("/dashboard/")
        assert nav_section_active(req, "dashboard") is True
        assert nav_section_active(req, "courses") is False


class TestDjangoSystemChecks:
    """Garante que nenhum check CRITICAL/ERROR existe na configuração."""

    def test_sem_erros_criticos(self):
        errors = checks.run_checks()
        criticos = [e for e in errors if e.level >= checks.ERROR]
        msgs = "\n".join(str(e) for e in criticos)
        assert not criticos, f"Django system checks falharam:\n{msgs}"


@pytest.mark.django_db
class TestLandingView:
    def test_landing_acessivel_para_anonimo(self, client):
        resp = client.get(reverse("core:landing"))
        assert resp.status_code == 200

    def test_landing_redireciona_admitido_para_dashboard(
        self, client, admitted_user
    ):
        client.force_login(admitted_user)
        resp = client.get(reverse("core:landing"))
        assert resp.status_code == 302
        assert resp.url == reverse("core:dashboard")

    def test_landing_nao_redireciona_pending(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.get(reverse("core:landing"))
        assert resp.status_code == 200


@pytest.mark.django_db
class TestDashboardView:
    def test_requer_login(self, client):
        resp = client.get(reverse("core:dashboard"))
        assert resp.status_code == 302

    def test_renderiza_para_admitido(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.get(reverse("core:dashboard"))
        assert resp.status_code == 200
        assert "phases" in resp.context
        assert "radar" in resp.context
        assert "leaderboard" in resp.context

    def test_pending_user_e_redirecionado_pelo_gate(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.get(reverse("core:dashboard"))
        assert resp.status_code == 302
        assert resp.url == reverse("assessments:start")

    def test_leaderboard_contacts_json_reflete_show_contact_info(
        self, client, make_user
    ):
        """Quem marcou exibir contato no perfil deve aparecer com show_contact true no JSON."""
        phase = Phase.objects.create(name="Fase LB", order=1)
        topic = Topic.objects.create(phase=phase, title="Tópico LB", order=1)
        aberto = make_user(
            email="contato-sim@example.com",
            show_in_leaderboard=True,
            show_contact_info=True,
            full_name="Aberto",
        )
        fechado = make_user(
            email="contato-nao@example.com",
            show_in_leaderboard=True,
            show_contact_info=False,
            full_name="Fechado",
        )
        TopicScore.objects.create(user=aberto, topic=topic, points=9, best_quiz_score=9)
        TopicScore.objects.create(
            user=fechado, topic=topic, points=5, best_quiz_score=5
        )
        viewer = make_user(email="viewer-lb@example.com")
        client.force_login(viewer)
        resp = client.get(reverse("core:dashboard"))
        assert resp.status_code == 200
        payload = json.loads(resp.context["leaderboard_contacts_json"])
        assert payload[str(aberto.pk)]["show_contact"] is True
        assert payload[str(fechado.pk)]["show_contact"] is False
        assert payload[str(aberto.pk)]["total"] == 9
        assert isinstance(payload[str(aberto.pk)]["total"], int)
        assert payload[str(aberto.pk)]["profile_url"] == reverse(
            "accounts:profile", args=[aberto.pk]
        )
        body = resp.content.decode()
        # Terceiro argumento = mesmos pts da linha (inteiro, sem localização)
        assert f"select('{aberto.pk}', true, 9)" in body
        assert f"select('{fechado.pk}', false, 5)" in body


@pytest.mark.django_db
class TestDonationView:
    def test_donation_acessivel_para_anonimo(self, client):
        resp = client.get(reverse("donations:index"))
        assert resp.status_code == 200

    def test_donation_acessivel_para_pending(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.get(reverse("donations:index"))
        assert resp.status_code == 200


@pytest.mark.django_db
class TestDonationContextProcessor:
    def test_context_inclui_donation_label_e_url(self, client):
        resp = client.get(reverse("core:landing"))
        assert "DONATION_URL" in resp.context
        assert "DONATION_LABEL" in resp.context
