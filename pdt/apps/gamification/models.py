"""Pontuação por tópico, tentativas de quiz e bonus por ajuda concedida."""
from __future__ import annotations

from django.conf import settings
from django.db import models, transaction


class TopicAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_attempts"
    )
    topic = models.ForeignKey(
        "courses.Topic", on_delete=models.CASCADE, related_name="attempts"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveSmallIntegerField(default=10)
    score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.user} → {self.topic} ({self.score}/{self.total_questions})"


class TopicAttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        TopicAttempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey("courses.Question", on_delete=models.CASCADE)
    choice = models.ForeignKey(
        "courses.Choice", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_correct = models.BooleanField(default=False)


class TopicScore(models.Model):
    """Snapshot do melhor desempenho do usuário em cada tópico.

    `points` agrega tanto a melhor pontuação de quiz quanto bônus por ajuda
    concedida no mapa, para representar bem o eixo no radar.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_scores"
    )
    topic = models.ForeignKey(
        "courses.Topic", on_delete=models.CASCADE, related_name="topic_scores"
    )
    best_quiz_score = models.PositiveSmallIntegerField(default=0)
    help_bonus = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "topic")]
        ordering = ["topic_id"]

    def __str__(self) -> str:
        return f"{self.user} · {self.topic} · {self.points} pts"

    def recompute(self) -> None:
        self.points = self.best_quiz_score + self.help_bonus
        self.save(update_fields=["points", "updated_at"])

    @classmethod
    @transaction.atomic
    def update_from_attempt(cls, attempt: TopicAttempt) -> "TopicScore":
        score, _ = cls.objects.get_or_create(user=attempt.user, topic=attempt.topic)
        if attempt.score > score.best_quiz_score:
            score.best_quiz_score = attempt.score
        score.points = score.best_quiz_score + score.help_bonus
        score.save()
        return score

    @classmethod
    @transaction.atomic
    def add_help_bonus(cls, *, user, topic, amount: int = 1) -> "TopicScore":
        score, _ = cls.objects.get_or_create(user=user, topic=topic)
        score.help_bonus = (score.help_bonus or 0) + amount
        score.points = score.best_quiz_score + score.help_bonus
        score.save()
        return score
