"""Fixtures globais usadas em toda a suíte de testes."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def make_user(db):
    """Factory para criar usuários, admitidos por padrão."""

    counter = {"i": 0}

    def _make(
        *,
        email: str | None = None,
        password: str = "test-pass-1234",
        admission_passed: bool = True,
        is_staff: bool = False,
        full_name: str = "",
        show_in_leaderboard: bool = False,
        show_contact_info: bool = False,
        show_on_map: bool = True,
        help_notifications_enabled: bool = True,
    ):
        counter["i"] += 1
        if email is None:
            email = f"user{counter['i']}@example.com"
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name or f"User {counter['i']}",
            admission_passed=admission_passed,
            is_staff=is_staff,
            show_in_leaderboard=show_in_leaderboard,
            show_contact_info=show_contact_info,
            show_on_map=show_on_map,
            help_notifications_enabled=help_notifications_enabled,
        )
        return user

    return _make


@pytest.fixture
def admitted_user(make_user):
    return make_user(email="admitted@example.com", admission_passed=True)


@pytest.fixture
def pending_user(make_user):
    return make_user(email="pending@example.com", admission_passed=False)


@pytest.fixture
def auth_client(client, admitted_user):
    client.force_login(admitted_user)
    return client


@pytest.fixture
def seed_phases(db):
    """Cria 1 fase + 1 tópico mínimos com lesson + 10 questões para uso em testes."""
    from apps.courses.models import Choice, Lesson, Phase, Question, Topic

    phase = Phase.objects.create(
        name="Fase de Teste", description="Fase usada nos testes", order=1
    )
    topic = Topic.objects.create(
        phase=phase, title="Tópico de Teste", summary="Tópico de teste", order=1
    )
    Lesson.objects.create(topic=topic, intro="i", body="b", practical="p")
    questions = []
    for i in range(10):
        q = Question.objects.create(
            topic=topic, statement=f"Pergunta {i}", explanation="exp", order=i
        )
        Choice.objects.create(question=q, text=f"Correta {i}", is_correct=True, order=0)
        Choice.objects.create(question=q, text=f"Errada {i}", is_correct=False, order=1)
        questions.append(q)
    return {"phase": phase, "topic": topic, "questions": questions}
