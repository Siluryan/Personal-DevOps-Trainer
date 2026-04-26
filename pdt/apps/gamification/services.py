"""Funções utilitárias para radar e ranking."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Sum, Value
from django.db.models.functions import Coalesce

from apps.courses.models import Topic

from .models import TopicScore

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
