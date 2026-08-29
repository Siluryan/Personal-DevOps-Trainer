"""Popula o banco com as 300 questões do simulador de entrevistas.

Idempotente: ao rodar de novo, atualiza os textos das questões existentes pela
ordem dentro de cada nível.

As alternativas são embaralhadas de forma **determinística** e com entropia
crescente por nível:

- **Júnior**: apenas nível + ordem da questão (baseline).
- **Pleno**: soma impressão digital do enunciado e do texto da alternativa
  correta (o fonte ainda tem viés, ex.: ~49% com gabarito na posição 1).
- **Sênior**: mesma base do pleno + rodada extra de mistura (mais sensível ao
  conteúdo, menos previsível só pelo índice).

Assim a letra correta deixa de ficar concentrada na mesma posição e o “chute
fixo” perde força; no sênior o permutador depende mais do texto da questão.
"""
from __future__ import annotations

import hashlib
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.interviews.models import InterviewQuestion
from apps.interviews.seed_data import ALL_INTERVIEW_QUESTIONS

_SHUFFLE_VERSION = "pdt-interview-choice-shuffle-v2"


def _shuffle_seed_int(level: str, order: int, statement: str, correct_text: str) -> int:
    """Semente do RNG: mais dependente de conteúdo conforme o nível sobe."""
    base = hashlib.sha256(
        f"{_SHUFFLE_VERSION}|{level}|{order}".encode("utf-8")
    ).digest()
    content = hashlib.sha256(
        (statement + "\n" + correct_text).encode("utf-8")
    ).digest()

    if level == "junior":
        material = base
    elif level == "pleno":
        material = hashlib.sha256(base + content + b"|pleno-tier").digest()
    elif level == "senior":
        mid = hashlib.sha256(base + content + b"|senior-tier").digest()
        material = hashlib.sha256(mid + content + base + b"|senior-deep").digest()
    else:
        material = hashlib.sha256(base + content + b"|" + level.encode()).digest()

    return int.from_bytes(material[:16], "big")


def _deterministic_shuffle_choices(
    level: str,
    order: int,
    statement: str,
    choices: list[str],
    correct_idx: int,
) -> tuple[list[str], int, list[int]]:
    """Retorna também `permutation`: para cada posição nova, o índice original —
    usado por quem chama pra reordenar `choices_en` (mesma ordem, ver EN)."""
    n = len(choices)
    if not 0 <= correct_idx < n:
        raise ValueError("correct_index fora do intervalo")
    correct_text = choices[correct_idx]
    rng = random.Random(
        _shuffle_seed_int(level, order, statement, correct_text)
    )
    permutation = list(range(n))
    rng.shuffle(permutation)
    out = [choices[i] for i in permutation]
    try:
        new_idx = out.index(correct_text)
    except ValueError as e:
        raise ValueError(
            "texto da alternativa correta ambíguo ou duplicado após embaralhar"
        ) from e
    return out, new_idx, permutation


class Command(BaseCommand):
    help = "Cria/atualiza as questões do simulador de entrevistas (júnior, pleno, sênior)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-shuffle",
            action="store_true",
            help=(
                "Mantém a ordem das alternativas igual ao arquivo fonte (só para "
                "depuração; em produção deixe o padrão para evitar viés de posição)."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        no_shuffle = options["no_shuffle"]
        total = 0
        for level, questions in ALL_INTERVIEW_QUESTIONS.items():
            existing = list(
                InterviewQuestion.objects.filter(level=level).order_by("order", "id")
            )
            for idx, data in enumerate(questions):
                choices = list(data["choices"])
                choices_en_src = data.get("choices_en")
                correct_idx = int(data["correct_index"])
                statement = data["statement"]
                if not no_shuffle:
                    choices, correct_idx, permutation = _deterministic_shuffle_choices(
                        level, idx, statement, choices, correct_idx
                    )
                    choices_en = (
                        [choices_en_src[i] for i in permutation] if choices_en_src else None
                    )
                else:
                    choices_en = choices_en_src

                if idx < len(existing):
                    q = existing[idx]
                    q.category = data.get("category", "")
                    q.statement = statement
                    q.statement_en = data.get("statement_en", "")
                    q.choices = choices
                    q.choices_en = choices_en
                    q.correct_index = correct_idx
                    q.explanation = data.get("explanation", "")
                    q.explanation_en = data.get("explanation_en", "")
                    q.order = idx
                    q.is_active = True
                    q.save()
                else:
                    InterviewQuestion.objects.create(
                        level=level,
                        category=data.get("category", ""),
                        statement=statement,
                        statement_en=data.get("statement_en", ""),
                        choices=choices,
                        choices_en=choices_en,
                        correct_index=correct_idx,
                        explanation=data.get("explanation", ""),
                        explanation_en=data.get("explanation_en", ""),
                        order=idx,
                        is_active=True,
                    )
                total += 1

            extras = existing[len(questions) :]
            for extra in extras:
                extra.is_active = False
                extra.save(update_fields=["is_active"])

        self.stdout.write(
            self.style.SUCCESS(
                f"OK, {total} questões sincronizadas (júnior + pleno + sênior)."
            )
        )
