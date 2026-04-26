"""Testes do app courses: modelos, quiz, integridade dos dados de seed."""
from __future__ import annotations

import pytest
from django.urls import reverse

from apps.courses.models import Choice, Phase, Question, Topic
from apps.courses.seed_data import PHASES
from apps.gamification.models import TopicAttempt, TopicScore


@pytest.mark.django_db
class TestPhaseAndTopicModels:
    def test_phase_str_e_slug_automatico(self):
        phase = Phase.objects.create(name="Fase X", order=42)
        assert "Fase 42" in str(phase)
        assert phase.slug == "fase-x"

    def test_topic_slug_automatico_e_get_absolute_url(self):
        phase = Phase.objects.create(name="Fase Y", order=2)
        topic = Topic.objects.create(phase=phase, title="Hardening Linux", order=1)
        assert topic.slug == "hardening-linux"
        assert topic.get_absolute_url() == reverse(
            "courses:topic_detail", args=["hardening-linux"]
        )

    def test_topic_unique_phase_order(self):
        from django.db import IntegrityError, transaction

        phase = Phase.objects.create(name="Fase Z", order=3)
        Topic.objects.create(phase=phase, title="A", order=1)
        with pytest.raises(IntegrityError), transaction.atomic():
            Topic.objects.create(phase=phase, title="B", order=1)


class TestSeedDataIntegrity:
    """Garante que o conteúdo das 6 fases está bem-formado."""

    def test_existem_6_fases(self):
        assert len(PHASES) == 6

    def test_cada_fase_tem_10_topicos(self):
        for i, phase in enumerate(PHASES, start=1):
            assert len(phase["topics"]) == 10, (
                f"Fase {i} tem {len(phase['topics'])} tópicos (esperava 10)"
            )

    def test_cada_topico_tem_no_minimo_5_materiais(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                materials = topic.get("materials", [])
                assert len(materials) >= 5, (
                    f"{topic['title']} tem só {len(materials)} materiais"
                )

    def test_cada_topico_tem_10_questoes_com_unica_correta(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                questions = topic.get("questions", [])
                assert len(questions) == 10, (
                    f"{topic['title']} tem {len(questions)} questões (esperava 10)"
                )
                for qi, q in enumerate(questions):
                    correct = [c for c in q["choices"] if c.get("correct")]
                    assert len(correct) == 1, (
                        f"{topic['title']} Q{qi}: deve ter exatamente 1 alternativa correta"
                    )

    def test_alternativas_nao_estao_sempre_na_primeira_posicao(self):
        """A correta não pode ser sempre índice 0, exige embaralhamento."""
        first_position_count = 0
        total = 0
        for phase in PHASES:
            for topic in phase["topics"]:
                for q in topic.get("questions", []):
                    total += 1
                    if q["choices"][0].get("correct"):
                        first_position_count += 1
        # Com 500 questões embaralhadas, a taxa na posição 0 deve ser ~25%
        # (1 em 4). Aceitamos até 40%, se passar disso o shuffle não está
        # funcionando. Na prática fica em torno de 25%.
        ratio = first_position_count / total
        assert ratio < 0.40, (
            f"Alternativa correta está na posição 0 em {ratio:.0%} das questões; "
            f"o embaralhamento não está funcionando."
        )

    def test_lessons_tem_intro_body_e_practical_preenchidos(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                lesson = topic.get("lesson", {})
                for key in ("intro", "body", "practical"):
                    assert lesson.get(key), (
                        f"{topic['title']} sem '{key}' na aula"
                    )

    def test_titulos_de_topico_sao_unicos(self):
        seen = set()
        for phase in PHASES:
            for topic in phase["topics"]:
                assert topic["title"] not in seen, f"Tópico duplicado: {topic['title']}"
                seen.add(topic["title"])
        assert len(seen) == 60


@pytest.mark.django_db
class TestSeedTopicsCommand:
    """Verifica que o management command importa o conteúdo corretamente."""

    def test_seed_topics_cria_tudo(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        assert Phase.objects.count() == 6
        assert Topic.objects.count() == 60
        assert Question.objects.count() == 600  # 60 tópicos × 10 perguntas
        for question in Question.objects.all():
            assert question.choices.filter(is_correct=True).count() == 1

    def test_seed_topics_idempotente(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        primeiro_count = Topic.objects.count()
        call_command("seed_topics", verbosity=0)
        assert Topic.objects.count() == primeiro_count


@pytest.mark.django_db
class TestQuizFlow:
    """Fluxo completo do quiz: GET → POST com respostas → result + score."""

    def test_quiz_renderiza_para_admitido(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        url = reverse("courses:quiz", args=[seed_phases["topic"].slug])
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"Pergunta 0" in resp.content

    def test_quiz_acerto_total_atualiza_topic_score(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {}
        for q in seed_phases["questions"]:
            correct = q.choices.get(is_correct=True)
            post_data[f"q_{q.id}"] = correct.id

        resp = client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        assert resp.status_code == 302

        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 10
        assert attempt.finished_at is not None

        score = TopicScore.objects.get(user=admitted_user, topic=topic)
        assert score.best_quiz_score == 10
        assert score.points == 10

    def test_quiz_acerto_parcial(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {}
        for i, q in enumerate(seed_phases["questions"]):
            if i < 7:
                ch = q.choices.get(is_correct=True)
            else:
                ch = q.choices.get(is_correct=False)
            post_data[f"q_{q.id}"] = ch.id

        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 7

    def test_quiz_resposta_em_branco(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        client.post(reverse("courses:quiz", args=[topic.slug]), {})
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 0

    def test_quiz_so_atualiza_best_score_se_for_maior(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]

        # Tentativa 1: 10/10
        post_data_perfeito = {
            f"q_{q.id}": q.choices.get(is_correct=True).id
            for q in seed_phases["questions"]
        }
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data_perfeito)

        # Tentativa 2: pior (3/10)
        post_data_ruim = {}
        for i, q in enumerate(seed_phases["questions"]):
            ch = q.choices.get(is_correct=True if i < 3 else False)
            post_data_ruim[f"q_{q.id}"] = ch.id
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data_ruim)

        score = TopicScore.objects.get(user=admitted_user, topic=topic)
        assert score.best_quiz_score == 10  # mantém o melhor

    def test_quiz_result_view_acessivel_apenas_para_dono(
        self, client, admitted_user, seed_phases, make_user
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {
            f"q_{q.id}": q.choices.get(is_correct=True).id
            for q in seed_phases["questions"]
        }
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)

        outro = make_user(email="outro@x.com")
        client.force_login(outro)
        url = reverse("courses:quiz_result", args=[topic.slug, attempt.id])
        resp = client.get(url)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestTopicViews:
    def test_track_view_lista_fases(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        resp = client.get(reverse("courses:track"))
        assert resp.status_code == 200
        assert b"Fase de Teste" in resp.content

    def test_topic_detail_view(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        url = reverse("courses:topic_detail", args=[seed_phases["topic"].slug])
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"T\xc3\xb3pico de Teste" in resp.content
