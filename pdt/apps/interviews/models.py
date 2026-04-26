"""Simulador de entrevistas: questões, tentativas e respostas.

Três níveis (junior, pleno, senior) com 100 questões cada. Cada usuário pode
ter no máximo uma tentativa em andamento (`finished_at` nulo) por nível, e
suas respostas ficam salvas em `answers` (dict question_id → choice_index)
para retomar de onde parou.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models


LEVEL_JUNIOR = "junior"
LEVEL_PLENO = "pleno"
LEVEL_SENIOR = "senior"
LEVEL_CHOICES = [
    (LEVEL_JUNIOR, "Júnior"),
    (LEVEL_PLENO, "Pleno"),
    (LEVEL_SENIOR, "Sênior"),
]
PASS_PERCENT = 80  # 80% para promover

QUESTIONS_PER_TEST = 100


class InterviewQuestion(models.Model):
    """Questão do banco de entrevistas, agrupada por nível e categoria."""

    level = models.CharField(max_length=12, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=80, blank=True)
    statement = models.TextField()
    choices = models.JSONField(
        default=list,
        help_text="Lista de strings com as alternativas, em ordem.",
    )
    correct_index = models.PositiveSmallIntegerField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["level", "order", "id"]
        indexes = [
            models.Index(fields=["level", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"[{self.level}] {self.statement[:60]}"


class InterviewAttempt(models.Model):
    """Tentativa do usuário em uma simulação de entrevista de um nível.

    Mantida 'em andamento' enquanto `finished_at` for nulo. As respostas são
    persistidas a cada questão respondida, o usuário pode sair e voltar.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_attempts",
    )
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    question_ids = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "level", "finished_at"]),
        ]

    def __str__(self) -> str:
        status = "concluído" if self.finished_at else "em andamento"
        return f"{self.user} · {self.level} · {status}"

    @property
    def total(self) -> int:
        return len(self.question_ids) or QUESTIONS_PER_TEST

    @property
    def answered_count(self) -> int:
        return len(self.answers or {})

    @property
    def progress_percent(self) -> int:
        t = self.total or 1
        return int(round(100 * self.answered_count / t))

    @property
    def score_percent(self) -> int:
        t = self.total or 1
        return int(round(100 * self.score / t))

    def next_unanswered_index(self) -> int:
        """Retorna o índice (0-based) da próxima questão sem resposta."""
        answered = set(str(qid) for qid in (self.answers or {}).keys())
        for i, qid in enumerate(self.question_ids):
            if str(qid) not in answered:
                return i
        return len(self.question_ids)
