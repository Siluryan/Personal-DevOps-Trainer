"""Cria (ou atualiza) um superusuário pronto para QA.

Uso típico (e-mail vindo do ambiente, sem valor fixo no código):

    export PDT_QA_SUPERUSER_EMAIL=qa@suaempresa.dev
    python manage.py create_qa_superuser

Ou explícito na linha de comando:

    python manage.py create_qa_superuser --email qa@suaempresa.dev

O comando é idempotente: se o e-mail já existe, atualiza os flags e troca a
senha por uma nova de 42 caracteres. Imprime e-mail e senha no stdout para que
sejam copiados na hora; a senha nunca é gravada em arquivo nem no repositório.

Flags habilitados:
    is_active, is_staff, is_superuser, admission_passed,
    show_in_leaderboard, show_contact_info, show_on_map,
    help_notifications_enabled.
Career level definido como Sênior, liberando todos os simulados.
"""
from __future__ import annotations

import os
import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Apenas chars que não exigem aspas/escape no shell — evita dor de cabeça em QA.
PASSWORD_ALPHABET = string.ascii_letters + string.digits + "@#-_+!"
PASSWORD_LENGTH = 42
QA_EMAIL_ENV = "PDT_QA_SUPERUSER_EMAIL"


def _generate_password(length: int = PASSWORD_LENGTH) -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(length))


class Command(BaseCommand):
    help = (
        "Cria (ou atualiza) um superusuário de QA com todos os flags habilitados "
        "e senha aleatória de 42 caracteres."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=None,
            help=(
                f"E-mail do superusuário QA. Se omitido, usa {QA_EMAIL_ENV} "
                "(defina no .env ou no shell)."
            ),
        )
        parser.add_argument(
            "--name",
            default="QA Admin",
            help="Nome completo a exibir no perfil (default: «QA Admin»).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        raw_email = options["email"] or os.environ.get(QA_EMAIL_ENV)
        if not raw_email or not str(raw_email).strip():
            raise CommandError(
                f"Informe --email ou defina a variável de ambiente {QA_EMAIL_ENV} "
                "(veja .env.example)."
            )
        email = User.objects.normalize_email(str(raw_email).strip())
        full_name = options["name"]

        defaults = dict(
            full_name=full_name,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            admission_passed=True,
            career_level=User.SENIOR,
            show_in_leaderboard=True,
            show_contact_info=True,
            show_on_map=True,
            help_notifications_enabled=True,
        )

        user, created = User.objects.update_or_create(email=email, defaults=defaults)

        password = _generate_password()
        user.set_password(password)
        user.save(update_fields=["password"])

        action = "criado" if created else "atualizado"
        bar = "=" * 60
        self.stdout.write(self.style.SUCCESS(bar))
        self.stdout.write(self.style.SUCCESS(f"Superusuário QA {action}."))
        self.stdout.write(f"e-mail : {email}")
        self.stdout.write(f"senha  : {password}")
        self.stdout.write(
            "flags  : is_active, is_staff, is_superuser, admission_passed, "
            "show_in_leaderboard, show_contact_info, show_on_map, "
            "help_notifications_enabled"
        )
        self.stdout.write(f"nível  : {user.career_label} ({user.career_level})")
        self.stdout.write(self.style.SUCCESS(bar))
        self.stdout.write(
            self.style.WARNING(
                "Guarde a senha agora: ela não é exibida novamente. "
                "Para gerar uma nova, rode o comando outra vez."
            )
        )
