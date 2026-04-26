"""Modelos do teste de admissão (Linux + Redes)."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class AdmissionQuestion(models.Model):
    """Banco de questões do teste de admissão."""

    LINUX = "linux"
    NETWORK = "network"
    AREA_CHOICES = [(LINUX, "Linux"), (NETWORK, "Redes")]

    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    statement = models.TextField()
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["area", "id"]

    def __str__(self) -> str:
        return f"[{self.get_area_display()}] {self.statement[:60]}"


class AdmissionChoice(models.Model):
    question = models.ForeignKey(
        AdmissionQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "order", "id"]

    def __str__(self) -> str:
        marker = "✓" if self.is_correct else "·"
        return f"{marker} {self.text}"


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
