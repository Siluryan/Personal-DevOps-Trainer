"""Modelos do teste de admissão (Linux + Redes)."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.i18n import localized


class AdmissionQuestion(models.Model):
    """Banco de questões do teste de admissão."""

    LINUX = "linux"
    NETWORK = "network"
    AREA_CHOICES = [(LINUX, _("Linux")), (NETWORK, _("Redes"))]

    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    statement = models.TextField()
    statement_en = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    explanation_en = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["area", "id"]

    def __str__(self) -> str:
        return f"[{self.get_area_display()}] {self.statement[:60]}"

    @property
    def display_statement(self) -> str:
        return localized(self.statement, self.statement_en)

    @property
    def display_explanation(self) -> str:
        return localized(self.explanation, self.explanation_en)


class AdmissionChoice(models.Model):
    question = models.ForeignKey(
        AdmissionQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=255)
    text_en = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "order", "id"]

    def __str__(self) -> str:
        marker = "✓" if self.is_correct else "·"
        return f"{marker} {self.text}"

    @property
    def display_text(self) -> str:
        return localized(self.text, self.text_en)


class AdmissionAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admission_attempts"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    question_ids = models.JSONField(default=list)
    answers = models.JSONField(default=dict)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        status = "aprovado" if self.passed else "reprovado"
        return f"{self.user} - {self.score}/10 ({status})"
