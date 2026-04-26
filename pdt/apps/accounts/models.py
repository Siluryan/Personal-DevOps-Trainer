"""Modelos de usuário do PDT.

O usuário customizado já carrega os campos exigidos pelo escopo do projeto
(LinkedIn, GitHub, etc.) e o flag `admission_passed`, que controla o acesso
às áreas internas.
"""
from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse


class UserManager(BaseUserManager):
    """Gerenciador de usuário baseado em e-mail."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("E-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("admission_passed", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser precisa de is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser precisa de is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Usuário do PDT identificado por e-mail."""

    INTERN = "estagiario"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    CAREER_CHOICES = [
        (INTERN, "Estagiário"),
        (JUNIOR, "Júnior"),
        (PLENO, "Pleno"),
        (SENIOR, "Sênior"),
    ]
    CAREER_ORDER = [INTERN, JUNIOR, PLENO, SENIOR]

    username = None
    email = models.EmailField("e-mail", unique=True)

    full_name = models.CharField("nome completo", max_length=150, blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    github_url = models.URLField("GitHub", blank=True)
    bio = models.TextField("bio curta", blank=True, max_length=500)
    country = models.CharField("país", max_length=80, blank=True)

    career_level = models.CharField(
        "nível de carreira",
        max_length=12,
        choices=CAREER_CHOICES,
        default=INTERN,
        help_text=(
            "Definido pelo simulador de entrevistas. Sobe ao atingir 80%+ no "
            "teste do próximo nível."
        ),
    )

    show_in_leaderboard = models.BooleanField(
        "aparecer no ranking público",
        default=False,
        help_text="Marque para liberar a exibição no ranking público.",
    )
    show_contact_info = models.BooleanField(
        "deixar informações de contato visíveis para outros usuários",
        default=False,
        help_text=(
            "Quando marcado, outros usuários podem ver seu LinkedIn, GitHub, país e bio "
            "(no ranking, na página pública do perfil e onde o seu nome for exibido com detalhes)."
        ),
    )
    show_on_map = models.BooleanField(
        "aparecer no mapa de presença",
        default=False,
        help_text=(
            "Necessário para aparecer no mapa e para usar «Pedir ajuda»: sem esta opção "
            "outros não veem seu pin e a plataforma não aceita novos pedidos de ajuda."
        ),
    )
    help_notifications_enabled = models.BooleanField(
        "receber notificações de ajuda",
        default=True,
        help_text=(
            "Quando marcado, você recebe avisos de novas mensagens/atualizações da sala "
            "de ajuda enquanto navega em outras seções da plataforma."
        ),
    )

    admission_passed = models.BooleanField("teste de admissão aprovado", default=False)
    admission_score = models.PositiveSmallIntegerField(
        "nota da admissão", null=True, blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self) -> str:  # pragma: no cover - representação trivial
        return self.full_name or self.email

    @property
    def display_name(self) -> str:
        return self.full_name or self.email.split("@")[0]

    @property
    def career_label(self) -> str:
        return self.get_career_level_display()

    def can_take_interview(self, level: str) -> bool:
        """Pode tentar `level` se já está em ≥ nível anterior."""
        if level not in self.CAREER_ORDER or level == self.INTERN:
            return False
        order = self.CAREER_ORDER
        target_idx = order.index(level)
        current_idx = order.index(self.career_level)
        return current_idx >= target_idx - 1

    def promote_if_eligible(self, level: str) -> bool:
        """Sobe career_level apenas se `level` for o próximo passo natural."""
        order = self.CAREER_ORDER
        if level not in order:
            return False
        new_idx = order.index(level)
        cur_idx = order.index(self.career_level)
        if new_idx == cur_idx + 1:
            self.career_level = level
            self.save(update_fields=["career_level"])
            return True
        return False

    def get_absolute_url(self) -> str:
        return reverse("accounts:profile", args=[self.pk])
