"""Pontuação por tópico: tentativas de quiz, bônus por ajuda e labs concluídos."""
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
    choice_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Snapshot do texto da alternativa marcada, gravado no momento da "
            "resposta. `choice` é FK para `courses.Choice` e vira NULL quando "
            "o seed apaga e recria as alternativas — sem este snapshot, o "
            "histórico de tentativas antigas passava a mostrar '(em branco)' "
            "para respostas que o usuário de fato tinha dado."
        ),
    )
    is_correct = models.BooleanField(default=False)

    @property
    def display_text(self) -> str:
        """Texto a mostrar na revisão: o snapshot, com fallback para o texto
        atual da Choice (registros antigos, antes deste campo existir)."""
        if self.choice_text:
            return self.choice_text
        if self.choice_id:
            return self.choice.text
        return ""


class TopicScore(models.Model):
    """Snapshot do melhor desempenho do usuário em cada tópico.

    `points` agrega a melhor pontuação de quiz, bônus por ajuda concedida no
    mapa e bônus por laboratório concluído, para representar bem o eixo no
    radar.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_scores"
    )
    topic = models.ForeignKey(
        "courses.Topic", on_delete=models.CASCADE, related_name="topic_scores"
    )
    best_quiz_score = models.PositiveSmallIntegerField(default=0)
    help_bonus = models.PositiveSmallIntegerField(default=0)
    lab_bonus = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "topic")]
        ordering = ["topic_id"]

    def __str__(self) -> str:
        return f"{self.user} · {self.topic} · {self.points} pts"

    def recompute(self) -> None:
        self.points = self.best_quiz_score + self.help_bonus + self.lab_bonus
        self.save(update_fields=["points", "updated_at"])

    @classmethod
    @transaction.atomic
    def update_from_attempt(cls, attempt: TopicAttempt) -> "TopicScore":
        score, _ = cls.objects.get_or_create(user=attempt.user, topic=attempt.topic)
        if attempt.score > score.best_quiz_score:
            score.best_quiz_score = attempt.score
        score.points = score.best_quiz_score + score.help_bonus + score.lab_bonus
        score.save()
        return score

    @classmethod
    @transaction.atomic
    def sync_lab_bonus(cls, *, user, topic) -> "TopicScore":
        """Recalcula `lab_bonus` a partir dos labs concluídos no tópico.

        Recomputa do zero em vez de incrementar: refazer um lab já concluído
        não deve render ponto de novo, e um lab desativado depois deixa de
        contar sozinho.
        """
        score, _ = cls.objects.get_or_create(user=user, topic=topic)
        done = LabCompletion.objects.filter(
            user=user, lab__topic=topic, lab__is_active=True
        ).count()
        score.lab_bonus = done * LAB_POINTS
        score.points = score.best_quiz_score + score.help_bonus + score.lab_bonus
        score.save()
        return score

    @classmethod
    @transaction.atomic
    def add_help_bonus(cls, *, user, topic, amount: int = 1) -> "TopicScore":
        score, _ = cls.objects.get_or_create(user=user, topic=topic)
        score.help_bonus = (score.help_bonus or 0) + amount
        score.points = score.best_quiz_score + score.help_bonus + score.lab_bonus
        score.save()
        return score


LAB_POINTS = 1
"""Pontos somados ao `TopicScore` por laboratório concluído.

Cada página da aula tem o próprio lab; 1 ponto por página reforça a
leitura sem rivalizar com o teto do quiz (10) no eixo do radar.
"""


class LabCompletion(models.Model):
    """Registro idempotente de que o usuário concluiu um laboratório.

    Guardar a conclusão (em vez de só somar ponto na hora) é o que permite
    `TopicScore.sync_lab_bonus` recomputar do zero — assim refazer o mesmo
    lab não acumula ponto.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lab_completions"
    )
    lab = models.ForeignKey(
        "courses.Lab", on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "lab")]
        ordering = ["-completed_at"]
        verbose_name = "conclusão de laboratório"
        verbose_name_plural = "conclusões de laboratório"

    def __str__(self) -> str:
        return f"{self.user} concluiu {self.lab}"
