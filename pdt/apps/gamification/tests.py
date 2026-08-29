"""Testes do app gamification: radar, ranking, bonus de ajuda."""
from __future__ import annotations

import pytest
from django.urls import reverse

from apps.courses.models import Lab, Phase, Topic
from apps.gamification.models import LabCompletion, TopicAttempt, TopicScore
from apps.gamification.services import (
    build_radar_payload,
    top_users,
    total_score_for,
)


@pytest.fixture
def two_topics(db):
    phase = Phase.objects.create(name="Fase Test", order=1)
    t1 = Topic.objects.create(phase=phase, title="T1", order=1)
    t2 = Topic.objects.create(phase=phase, title="T2", order=2)
    return phase, t1, t2


@pytest.mark.django_db
class TestTopicScoreModel:
    def test_recompute_soma_quiz_e_help(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        score = TopicScore.objects.create(
            user=admitted_user, topic=t1, best_quiz_score=8, help_bonus=2
        )
        score.recompute()
        score.refresh_from_db()
        assert score.points == 10

    def test_update_from_attempt_so_aumenta(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        a1 = TopicAttempt.objects.create(user=admitted_user, topic=t1, score=7)
        TopicScore.update_from_attempt(a1)
        a2 = TopicAttempt.objects.create(user=admitted_user, topic=t1, score=4)
        TopicScore.update_from_attempt(a2)
        score = TopicScore.objects.get(user=admitted_user, topic=t1)
        assert score.best_quiz_score == 7

    def test_add_help_bonus_acumula(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        TopicScore.add_help_bonus(user=admitted_user, topic=t1, amount=2)
        TopicScore.add_help_bonus(user=admitted_user, topic=t1, amount=3)
        score = TopicScore.objects.get(user=admitted_user, topic=t1)
        assert score.help_bonus == 5
        assert score.points == 5

    def test_pontos_combinam_quiz_e_bonus(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        attempt = TopicAttempt.objects.create(user=admitted_user, topic=t1, score=8)
        TopicScore.update_from_attempt(attempt)
        TopicScore.add_help_bonus(user=admitted_user, topic=t1, amount=2)
        score = TopicScore.objects.get(user=admitted_user, topic=t1)
        assert score.points == 10

    def test_sync_lab_bonus_conta_labs_concluidos(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        lab1 = Lab.objects.create(topic=t1, kind="terminal", title="L1", spec={}, lesson_page=1)
        lab2 = Lab.objects.create(topic=t1, kind="order", title="L2", spec={}, lesson_page=2)
        LabCompletion.objects.create(user=admitted_user, lab=lab1)
        LabCompletion.objects.create(user=admitted_user, lab=lab2)
        score = TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)
        assert score.lab_bonus == 2  # 2 labs x LAB_POINTS (1)
        assert score.points == 2

    def test_sync_lab_bonus_ignora_lab_de_outro_topico(self, admitted_user, two_topics):
        _, t1, t2 = two_topics
        lab_outro = Lab.objects.create(topic=t2, kind="terminal", title="L", spec={})
        LabCompletion.objects.create(user=admitted_user, lab=lab_outro)
        score = TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)
        assert score.lab_bonus == 0

    def test_sync_lab_bonus_ignora_lab_inativo(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        lab = Lab.objects.create(topic=t1, kind="terminal", title="L", spec={}, is_active=False)
        LabCompletion.objects.create(user=admitted_user, lab=lab)
        score = TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)
        assert score.lab_bonus == 0

    def test_sync_lab_bonus_recomputa_do_zero_nao_acumula(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        lab = Lab.objects.create(topic=t1, kind="terminal", title="L", spec={})
        LabCompletion.objects.create(user=admitted_user, lab=lab)
        TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)
        score = TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)  # roda 2x
        assert score.lab_bonus == 1  # não dobra por rodar de novo

    def test_pontos_combinam_quiz_help_e_lab(self, admitted_user, two_topics):
        _, t1, _ = two_topics
        attempt = TopicAttempt.objects.create(user=admitted_user, topic=t1, score=8)
        TopicScore.update_from_attempt(attempt)
        TopicScore.add_help_bonus(user=admitted_user, topic=t1, amount=2)
        lab = Lab.objects.create(topic=t1, kind="terminal", title="L", spec={})
        LabCompletion.objects.create(user=admitted_user, lab=lab)
        score = TopicScore.sync_lab_bonus(user=admitted_user, topic=t1)
        assert score.points == 8 + 2 + 1


@pytest.mark.django_db
class TestRadarPayload:
    def test_radar_inclui_todos_os_topicos_ordenados(self, admitted_user, two_topics):
        _, t1, t2 = two_topics
        TopicScore.objects.create(
            user=admitted_user, topic=t1, best_quiz_score=5, points=5
        )
        payload = build_radar_payload(admitted_user)
        assert payload["labels"] == ["T1", "T2"]
        assert payload["points"] == [5, 0]
        assert payload["max_per_axis"] == 10

    def test_radar_anonimo(self, two_topics):
        from django.contrib.auth.models import AnonymousUser

        payload = build_radar_payload(AnonymousUser())
        assert payload["labels"] == ["T1", "T2"]
        assert payload["points"] == [0, 0]

    def test_radar_usa_title_en_quando_idioma_en(self, two_topics):
        from django.contrib.auth.models import AnonymousUser
        from django.utils import translation

        _, t1, t2 = two_topics
        t1.title_en = "Topic One EN"
        t1.save(update_fields=["title_en"])
        t2.title_en = "Topic Two EN"
        t2.save(update_fields=["title_en"])
        with translation.override("en"):
            payload = build_radar_payload(AnonymousUser())
        assert payload["labels"] == ["Topic One EN", "Topic Two EN"]


@pytest.mark.django_db
class TestTotalScore:
    def test_total_score_soma_topic_scores(self, admitted_user, two_topics):
        _, t1, t2 = two_topics
        TopicScore.objects.create(user=admitted_user, topic=t1, points=7)
        TopicScore.objects.create(user=admitted_user, topic=t2, points=3)
        assert total_score_for(admitted_user) == 10

    def test_total_score_anonimo(self):
        from django.contrib.auth.models import AnonymousUser

        assert total_score_for(AnonymousUser()) == 0


@pytest.mark.django_db
class TestLeaderboard:
    def test_top_users_so_inclui_quem_optou_pelo_ranking(
        self, make_user, two_topics
    ):
        _, t1, _ = two_topics
        publico = make_user(
            email="publico@x.com",
            admission_passed=True,
            show_in_leaderboard=True,
        )
        privado = make_user(
            email="privado@x.com",
            admission_passed=True,
            show_in_leaderboard=False,
        )
        TopicScore.objects.create(user=publico, topic=t1, points=10)
        TopicScore.objects.create(user=privado, topic=t1, points=20)

        users = list(top_users())
        assert publico in users
        assert privado not in users

    def test_top_users_ordenado_por_pontuacao(self, make_user, two_topics):
        _, t1, t2 = two_topics
        a = make_user(email="a@x.com", show_in_leaderboard=True)
        b = make_user(email="b@x.com", show_in_leaderboard=True)
        TopicScore.objects.create(user=a, topic=t1, points=5)
        TopicScore.objects.create(user=b, topic=t1, points=3)
        TopicScore.objects.create(user=b, topic=t2, points=10)

        users = list(top_users())
        assert users[0] == b  # 13 pontos
        assert users[1] == a  # 5 pontos

    def test_top_users_exclui_usuario_sem_pontos(self, make_user):
        make_user(email="zero@x.com", show_in_leaderboard=True)
        assert list(top_users()) == []

    def test_top_users_exclui_quem_nao_passou_admissao(self, make_user, two_topics):
        _, t1, _ = two_topics
        u = make_user(
            email="x@x.com",
            admission_passed=False,
            show_in_leaderboard=True,
        )
        TopicScore.objects.create(user=u, topic=t1, points=10)
        assert list(top_users()) == []


@pytest.mark.django_db
class TestGamificationViews:
    def test_leaderboard_publico(self, client):
        resp = client.get(reverse("gamification:leaderboard"))
        assert resp.status_code == 200

    def test_ranking_nao_exibe_links_sem_show_contact_info(
        self, client, make_user, two_topics
    ):
        _, t1, _ = two_topics
        u = make_user(
            email="sem-contato-ranking@example.com",
            show_in_leaderboard=True,
            show_contact_info=False,
            full_name="Ranking Sem Contato",
        )
        u.linkedin_url = "https://linkedin.com/in/ranking-privado"
        u.github_url = "https://github.com/ranking-privado"
        u.save(update_fields=["linkedin_url", "github_url"])
        TopicScore.objects.create(user=u, topic=t1, points=10)
        resp = client.get(reverse("gamification:leaderboard"))
        assert resp.status_code == 200
        body = resp.content.decode()
        assert u.display_name in body
        assert "linkedin.com/in/ranking-privado" not in body.lower()
        assert "github.com/ranking-privado" not in body.lower()

    def test_radar_requer_login(self, client):
        resp = client.get(reverse("gamification:radar"))
        assert resp.status_code == 302

    def test_radar_para_admitido(self, client, admitted_user):
        client.force_login(admitted_user)
        resp = client.get(reverse("gamification:radar"))
        assert resp.status_code == 200
