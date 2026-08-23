"""Testes do app courses: modelos, quiz, integridade dos dados de seed."""
from __future__ import annotations

import pytest
from django.urls import reverse

from apps.courses.models import Choice, Lab, Lesson, Phase, Question, Topic
from apps.courses.seed_data import PHASES
from apps.courses.seed_data.labs import LABS
from apps.gamification.models import LabCompletion, TopicAttempt, TopicScore

ALL_TOPIC_TITLES = {t["title"] for phase in PHASES for t in phase["topics"]}


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


class TestLabDataIntegrity:
    """Garante que os 60 laboratórios (1 por tópico) estão bem-formados.

    Cobre a queixa "não tem laboratório prático de verdade": cada um dos 60
    tópicos precisa ter exatamente 1 lab, com `topic_title` batendo com um
    tópico real (senão `seed_labs` levanta CommandError silenciosamente
    ignorável em produção) e `spec` no formato que `kind` espera.
    """

    def test_existem_60_labs_um_por_topico(self):
        assert len(LABS) == 60

    def test_topic_title_bate_com_topico_real(self):
        for lab in LABS:
            assert lab["topic_title"] in ALL_TOPIC_TITLES, (
                f"Lab {lab['title']!r} aponta pro tópico "
                f"{lab['topic_title']!r}, que não existe em seed_data"
            )

    def test_cada_topico_tem_exatamente_1_lab(self):
        titles = [lab["topic_title"] for lab in LABS]
        assert len(titles) == len(set(titles)) == 60

    def test_kind_e_um_dos_validos(self):
        validos = {k for k, _ in Lab.Kind.choices}
        for lab in LABS:
            assert lab["kind"] in validos, f"{lab['title']}: kind {lab['kind']!r} inválido"

    def test_spec_terminal_tem_pool_sem_token_duplicado(self):
        for lab in LABS:
            if lab["kind"] != "terminal":
                continue
            spec = lab["spec"]
            pool = spec["correct_command"] + spec["distractor_tokens"]
            assert len(set(pool)) == len(pool), f"{lab['title']}: token duplicado no pool"

    def test_spec_find_flaw_indice_dentro_do_range(self):
        for lab in LABS:
            if lab["kind"] != "find_flaw":
                continue
            spec = lab["spec"]
            assert 0 <= spec["flaw_line_index"] < len(spec["lines"]), lab["title"]

    def test_spec_order_mesmos_itens_embaralhados_e_ordenados(self):
        for lab in LABS:
            if lab["kind"] != "order":
                continue
            spec = lab["spec"]
            assert sorted(spec["steps_shuffled"]) == sorted(spec["correct_order"]), lab["title"]

    def test_spec_blanks_marcador_aparece_no_template(self):
        for lab in LABS:
            if lab["kind"] != "blanks":
                continue
            spec = lab["spec"]
            for key, blank in spec["blanks"].items():
                assert f"___{key}___" in spec["template"], f"{lab['title']}: falta marcador {key}"
                assert blank["correct"] in blank["options"], lab["title"]

    def test_spec_scenario_tem_exatamente_1_choice_boa(self):
        for lab in LABS:
            if lab["kind"] != "scenario":
                continue
            spec = lab["spec"]
            boas = sum(1 for c in spec["choices"] if c["good"])
            assert boas == 1, f"{lab['title']}: {boas} choices boas (esperava 1)"


@pytest.mark.django_db
class TestSeedLabsCommand:
    """Mesmo padrão de TestSeedTopicsCommand: idempotente, preserva edição."""

    def test_seed_labs_cria_um_por_topico(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        assert Lab.objects.count() == 60
        assert Topic.objects.filter(labs__isnull=True).count() == 0

    def test_seed_labs_idempotente(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        primeiro_count = Lab.objects.count()
        call_command("seed_labs", verbosity=0)
        assert Lab.objects.count() == primeiro_count

    def test_seed_labs_preserva_edicao_do_admin(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        lab = Lab.objects.first()
        lab.title = "Editado pelo mantenedor"
        lab.seed_managed = False
        lab.save(update_fields=["title", "seed_managed"])

        call_command("seed_labs", verbosity=0)
        lab.refresh_from_db()
        assert lab.title == "Editado pelo mantenedor"

    def test_seed_labs_force_sobrescreve_edicao(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        lab = Lab.objects.first()
        titulo_original = lab.title
        lab.title = "Será revertido"
        lab.seed_managed = False
        lab.save(update_fields=["title", "seed_managed"])

        call_command("seed_labs", force=True, verbosity=0)
        lab.refresh_from_db()
        assert lab.title == titulo_original
        assert lab.seed_managed is True


@pytest.mark.django_db
class TestLabCompleteView:
    def test_completar_lab_soma_bonus_e_e_idempotente(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        lab = Lab.objects.create(topic=topic, kind="terminal", title="L", spec={})

        url = reverse("courses:lab_complete", args=[lab.id])
        resp = client.post(url)
        assert resp.status_code == 200
        assert resp.json()["lab_bonus"] == 5
        assert LabCompletion.objects.filter(user=admitted_user, lab=lab).count() == 1

        resp2 = client.post(url)  # refazer não deve dobrar o bônus
        assert resp2.json()["lab_bonus"] == 5
        assert LabCompletion.objects.filter(user=admitted_user, lab=lab).count() == 1

    def test_completar_lab_exige_login(self, client, seed_phases):
        topic = seed_phases["topic"]
        lab = Lab.objects.create(topic=topic, kind="terminal", title="L", spec={})
        resp = client.post(reverse("courses:lab_complete", args=[lab.id]))
        assert resp.status_code in (302, 401, 403)

    def test_lab_inativo_nao_pode_ser_completado(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        lab = Lab.objects.create(
            topic=topic, kind="terminal", title="L", spec={}, is_active=False
        )
        resp = client.post(reverse("courses:lab_complete", args=[lab.id]))
        assert resp.status_code == 404


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

    def test_seed_topics_preserva_aula_editada_pelo_admin(self):
        """O defeito original: o seed rodava no boot do container e apagava
        qualquer edição feita pelo admin todo dia. `seed_managed=False`
        (setado automaticamente ao salvar pelo admin, ver apps.courses.admin)
        faz o próximo `seed_topics` pular esse registro."""
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        lesson = Lesson.objects.first()
        lesson.body = "<p>Texto editado manualmente pelo mantenedor.</p>"
        lesson.seed_managed = False
        lesson.save(update_fields=["body", "seed_managed"])

        call_command("seed_topics", verbosity=0)
        lesson.refresh_from_db()
        assert lesson.body == "<p>Texto editado manualmente pelo mantenedor.</p>"

    def test_seed_topics_force_sobrescreve_edicao(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        lesson = Lesson.objects.first()
        body_original = lesson.body
        lesson.body = "<p>Editado, mas será revertido por --force.</p>"
        lesson.seed_managed = False
        lesson.save(update_fields=["body", "seed_managed"])

        call_command("seed_topics", force=True, verbosity=0)
        lesson.refresh_from_db()
        assert lesson.body == body_original
        assert lesson.seed_managed is True

    def test_seed_topics_preserva_questao_e_suas_alternativas_editadas(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        question = Question.objects.first()
        choice_ids_antes = set(question.choices.values_list("id", flat=True))
        question.statement = "Enunciado corrigido pelo mantenedor."
        question.seed_managed = False
        question.save(update_fields=["statement", "seed_managed"])

        call_command("seed_topics", verbosity=0)
        question.refresh_from_db()
        assert question.statement == "Enunciado corrigido pelo mantenedor."
        # As Choice não foram apagadas/recriadas: mesmos IDs de antes.
        assert set(question.choices.values_list("id", flat=True)) == choice_ids_antes


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

    def test_resultado_sobrevive_a_alternativa_apagada_pelo_seed(
        self, client, admitted_user, seed_phases
    ):
        """Regressão: `choice` é SET_NULL. Antes do snapshot, rodar o seed
        (que apaga e recria as alternativas de uma questão) fazia o histórico
        de tentativas antigas mostrar "(em branco)" para respostas que o
        usuário de fato tinha dado — mesmo sem o usuário ter feito nada."""
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        question = seed_phases["questions"][0]
        picked = question.choices.get(is_correct=True)
        texto_respondido = picked.text

        # Responde tudo (não só a questão do teste): as outras 9 legitimamente
        # apareceriam como "(em branco)" se deixadas sem resposta, o que
        # confundiria uma checagem ingênua de substring na página inteira.
        post_data = {f"q_{question.id}": picked.id}
        for outra in seed_phases["questions"][1:]:
            post_data[f"q_{outra.id}"] = outra.choices.get(is_correct=True).id
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)

        # Simula o que `seed_topics` faz com uma questão seed_managed=True:
        # apaga todas as Choice da questão.
        question.choices.all().delete()

        resp = client.get(reverse("courses:quiz_result", args=[topic.slug, attempt.id]))
        assert resp.status_code == 200
        assert texto_respondido.encode() in resp.content

        resposta = attempt.answers.get(question=question)
        assert resposta.choice_id is None  # a Choice foi apagada de verdade
        assert resposta.display_text == texto_respondido
        assert b"(em branco)" not in resp.content


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
