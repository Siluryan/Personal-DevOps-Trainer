"""Testes do app core: landing, dashboard, doação e context processor."""
from __future__ import annotations

import pytest
from django.core import checks
from django.urls import reverse


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
