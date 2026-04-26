"""Popula o banco com as 300 questões do simulador de entrevistas.

Idempotente: ao rodar de novo, atualiza os textos das questões existentes pela
ordem dentro de cada nível.
"""
from __future__ import annotations

import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.interviews.models import InterviewQuestion
from apps.interviews.seed_data import ALL_INTERVIEW_QUESTIONS


class Command(BaseCommand):
    help = "Cria/atualiza as questões do simulador de entrevistas (júnior, pleno, sênior)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--shuffle",
            action="store_true",
            help="Embaralha a ordem das alternativas (mantendo correct_index correto).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        shuffle = options["shuffle"]
        total = 0
        for level, questions in ALL_INTERVIEW_QUESTIONS.items():
            existing = list(
                InterviewQuestion.objects.filter(level=level).order_by("order", "id")
            )
            for idx, data in enumerate(questions):
                choices = list(data["choices"])
                correct_idx = int(data["correct_index"])
                correct_text = choices[correct_idx]
                if shuffle:
                    random.shuffle(choices)
                    correct_idx = choices.index(correct_text)

                if idx < len(existing):
                    q = existing[idx]
                    q.category = data.get("category", "")
                    q.statement = data["statement"]
                    q.choices = choices
                    q.correct_index = correct_idx
                    q.explanation = data.get("explanation", "")
                    q.order = idx
                    q.is_active = True
                    q.save()
                else:
                    InterviewQuestion.objects.create(
                        level=level,
                        category=data.get("category", ""),
                        statement=data["statement"],
                        choices=choices,
                        correct_index=correct_idx,
                        explanation=data.get("explanation", ""),
                        order=idx,
                        is_active=True,
                    )
                total += 1

            extras = existing[len(questions):]
            for extra in extras:
                extra.is_active = False
                extra.save(update_fields=["is_active"])

        self.stdout.write(
            self.style.SUCCESS(
                f"OK, {total} questões sincronizadas (júnior + pleno + sênior)."
            )
        )
