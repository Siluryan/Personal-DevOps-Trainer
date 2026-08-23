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

    def test_display_name_usa_full_name_quando_preenchido(self):
        user = User.objects.create_user(email="ana@x.com", password="x", full_name="Ana")
        assert user.display_name == "Ana"

    def test_display_name_nunca_deriva_do_email(self):
        """Regressão: `display_name` é público e não pode expor o endereço.

        Antes caía em `email.split("@")[0]`, vazando a parte local no ranking,
        no mapa, no chat de ajuda e na página de perfil.
        """
        outro = User.objects.create_user(email="bruno@x.com", password="x")
        assert "bruno" not in outro.display_name
        assert "@" not in outro.display_name
        assert outro.display_name == f"Aluno #{outro.pk}"

    def test_display_name_ignora_full_name_em_branco(self):
        user = User.objects.create_user(email="carla@x.com", password="x", full_name="   ")
        assert "carla" not in user.display_name


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
                "help_notifications_enabled": True,
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
                "help_notifications_enabled": False,
            }
        )
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_setup_requer_login(self, client):
        resp = client.get(reverse("accounts:profile_setup"))
        assert resp.status_code == 302  # redireciona para login

    def test_profile_anonimo_nao_ve_quem_nao_optou(self, client, admitted_user):
        """Sem opt-in, visitante anônimo recebe 404 — não 403, não redirect.

        Devolver 404 é o que fecha a enumeração: a resposta fica idêntica à de
        um PK inexistente, então varrer /perfil/u/1..N não revela quem existe.
        """
        assert admitted_user.show_in_leaderboard is False
        resp = client.get(reverse("accounts:profile", args=[admitted_user.pk]))
        assert resp.status_code == 404

    def test_profile_anonimo_e_pk_inexistente_respondem_igual(
        self, client, admitted_user
    ):
        privado = client.get(reverse("accounts:profile", args=[admitted_user.pk]))
        inexistente = client.get(reverse("accounts:profile", args=[9_999_999]))
        assert privado.status_code == inexistente.status_code == 404

    def test_profile_anonimo_ve_quem_optou_pelo_ranking_publico(
        self, client, make_user
    ):
        publico = make_user(
            email="publico@example.com",
            full_name="Público",
            show_in_leaderboard=True,
        )
        resp = client.get(reverse("accounts:profile", args=[publico.pk]))
        assert resp.status_code == 200
        assert publico.display_name.encode() in resp.content

    def test_profile_logado_ve_qualquer_perfil(self, client, admitted_user, make_user):
        visitante = make_user(email="visitante-logado@example.com")
        client.force_login(visitante)
        resp = client.get(reverse("accounts:profile", args=[admitted_user.pk]))
        assert resp.status_code == 200
        assert admitted_user.display_name.encode() in resp.content

    def test_profile_sem_show_contact_oculta_urls_para_terceiros(
        self, client, make_user
    ):
        alvo = make_user(
            email="alvo@example.com",
            show_contact_info=False,
            full_name="Alvo",
        )
        alvo.linkedin_url = "https://linkedin.com/in/alvo-priv"
        alvo.github_url = "https://github.com/alvo-priv"
        alvo.save(update_fields=["linkedin_url", "github_url"])
        outro = make_user(email="visitante@example.com")
        client.force_login(outro)
        resp = client.get(reverse("accounts:profile", args=[alvo.pk]))
        assert resp.status_code == 200
        low = resp.content.decode().lower()
        assert "linkedin.com/in/alvo-priv" not in low
        assert "github.com/alvo-priv" not in low

    def test_profile_dono_nao_ve_links_com_show_contact_desligado(
        self, client, make_user
    ):
        u = make_user(
            email="dono@example.com",
            show_contact_info=False,
        )
        u.linkedin_url = "https://linkedin.com/in/dono"
        u.save(update_fields=["linkedin_url"])
        client.force_login(u)
        resp = client.get(reverse("accounts:profile", args=[u.pk]))
        assert b"linkedin.com/in/dono" not in resp.content.lower()
        assert b"editar perfil" in resp.content.lower()
