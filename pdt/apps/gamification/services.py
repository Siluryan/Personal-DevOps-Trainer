"""Funções utilitárias para radar e ranking."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Max, Sum, Value
from django.db.models.functions import Coalesce

from apps.courses.models import Topic

from .models import TopicAttempt, TopicScore

User = get_user_model()


def build_radar_payload(user) -> dict:
    """Monta o payload do radar (50 eixos) para um usuário."""
    topics = list(
        Topic.objects.select_related("phase").order_by("phase__order", "order")
    )
    user_scores = {}
    if user.is_authenticated:
        user_scores = {
            s.topic_id: s.points for s in TopicScore.objects.filter(user=user)
        }
    labels = [t.title for t in topics]
    points = [user_scores.get(t.id, 0) for t in topics]
    phases = [t.phase.name for t in topics]
    return {
        "labels": labels,
        "points": points,
        "phases": phases,
        "max_per_axis": 10,
    }


def total_score_for(user) -> int:
    if not user.is_authenticated:
        return 0
    return TopicScore.objects.filter(user=user).aggregate(total=Sum("points"))["total"] or 0


def top_users(limit: int = 50):
    """Retorna o top N de quem optou por aparecer no ranking."""
    _sync_topic_scores_for_public_users()
    qs = (
        User.objects.filter(show_in_leaderboard=True, admission_passed=True)
        .annotate(
            total=Coalesce(
                Sum("topic_scores__points"),
                Value(0),
                output_field=IntegerField(),
            )
        )
        .filter(total__gt=0)
        .order_by("-total", "-id")[:limit]
    )
    return qs


def _sync_topic_scores_for_public_users() -> None:
    """Reconciliador defensivo para produção.

    Em alguns cenários (deploys antigos/fluxos interrompidos), o snapshot
    `TopicScore.best_quiz_score` pode ficar atrás das tentativas já gravadas.
    Antes de renderizar o ranking, alinhamos o melhor score por tópico para os
    usuários públicos.
    """
    public_user_ids = list(
        User.objects.filter(show_in_leaderboard=True, admission_passed=True).values_list(
            "id", flat=True
        )
    )
    if not public_user_ids:
        return

    best_by_user_topic = (
        TopicAttempt.objects.filter(
            user_id__in=public_user_ids,
            finished_at__isnull=False,
        )
        .values("user_id", "topic_id")
        .annotate(best=Max("score"))
    )

    for row in best_by_user_topic:
        score, _ = TopicScore.objects.get_or_create(
            user_id=row["user_id"],
            topic_id=row["topic_id"],
        )
        best = int(row["best"] or 0)
        if best != score.best_quiz_score:
            score.best_quiz_score = best
            score.points = score.best_quiz_score + (score.help_bonus or 0)
            score.save(update_fields=["best_quiz_score", "points", "updated_at"])
