"""Testes do app accounts: modelo User, manager, middleware e perfis."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.forms import ProfileSetupForm
from apps.accounts.middleware import AdmissionGateMiddleware

User = get_user_model()


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_normaliza_email_e_define_senha(self):
        user = User.objects.create_user(email="JOAO@Example.COM", password="senha-segura-123")
        assert user.email == "JOAO@example.com"
        assert user.check_password("senha-segura-123")
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.admission_passed is False

    def test_create_user_sem_email_falha(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="x")

    def test_create_superuser_define_admission_passed(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="admin-123"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.admission_passed is True

    def test_display_name_usa_full_name_ou_local_part(self):
        user = User.objects.create_user(email="ana@x.com", password="x", full_name="Ana")
        assert user.display_name == "Ana"
        outro = User.objects.create_user(email="bruno@x.com", password="x")
        assert outro.display_name == "bruno"


@pytest.mark.django_db
class TestAdmissionGateMiddleware:
    """O middleware deve redirecionar usuários não-admitidos para o teste."""

    def test_usuario_nao_admitido_e_redirecionado_para_o_teste(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.get(reverse("courses:track"))
        assert resp.status_code == 302
        assert resp.url == reverse("assessments:start")

    def test_usuario_admitido_acessa_areas_internas(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.get(reverse("courses:track"))
        assert resp.status_code == 200

    def test_staff_passa_pelo_gate_mesmo_sem_admission(self, client, make_user):
        staff = make_user(is_staff=True, admission_passed=False)
        client.force_login(staff)
        resp = client.get(reverse("courses:track"))
        assert resp.status_code == 200

    def test_landing_e_admissao_sempre_acessiveis(self, client, pending_user):
        client.force_login(pending_user)
        for url_name in ["core:landing", "assessments:start", "donations:index"]:
            resp = client.get(reverse(url_name))
            assert resp.status_code == 200, f"{url_name} não está acessível"

    def test_anonimo_nao_e_afetado_pelo_gate(self, client):
        resp = client.get(reverse("core:landing"))
        assert resp.status_code == 200


@pytest.mark.django_db
class TestProfileSetupForm:
    def test_form_exige_linkedin_ou_github(self):
        form = ProfileSetupForm(
            data={
                "full_name": "Ana",
                "country": "Brasil",
                "bio": "",
                "linkedin_url": "",
                "github_url": "",
                "show_in_leaderboard": False,
                "show_on_map": True,
            }
        )
        assert not form.is_valid()
        assert "Informe ao menos um perfil profissional" in str(form.errors)

    def test_form_aceita_apenas_github(self):
        form = ProfileSetupForm(
            data={
                "full_name": "Ana",
                "country": "Brasil",
                "bio": "Desenvolvedora",
                "linkedin_url": "",
                "github_url": "https://github.com/ana",
                "show_in_leaderboard": False,
                "show_on_map": True,
            }
        )
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_setup_requer_login(self, client):
        resp = client.get(reverse("accounts:profile_setup"))
        assert resp.status_code == 302  # redireciona para login

    def test_profile_detail_visivel_publicamente(self, client, admitted_user):
        url = reverse("accounts:profile", args=[admitted_user.pk])
        resp = client.get(url)
        assert resp.status_code == 200
        assert admitted_user.display_name.encode() in resp.content
