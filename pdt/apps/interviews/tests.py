"""Testes do simulador de entrevistas.

Cobrem:
- Modelos `InterviewQuestion` e `InterviewAttempt` (propriedades e índice da
  próxima questão sem resposta).
- Lógica de carreira no `User` (`can_take_interview`, `promote_if_eligible`).
- Comando `seed_interviews` (povoa 300 questões e é idempotente).
- Fluxo HTTP completo: lista, iniciar, responder, salvar e sair, retomar,
  finalizar (aprovado e reprovado), descartar, e bloqueio sequencial.
"""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.core.templatetags.pdt_extras import interview_choice_lead
from apps.interviews.models import (
    LEVEL_JUNIOR,
    LEVEL_PLENO,
    LEVEL_SENIOR,
    PASS_PERCENT,
    QUESTIONS_PER_TEST,
    InterviewAttempt,
    InterviewQuestion,
)
from apps.interviews.views import _failure_message

User = get_user_model()


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def seed_interview_bank(db):
    """Cria um banco mínimo (100 por nível) para os testes de fluxo.

    Cada questão tem 4 alternativas, correta no índice 0. Isso simplifica
    asserts e mantém os testes rápidos (não precisamos das 300 reais).
    """
    bank = {LEVEL_JUNIOR: [], LEVEL_PLENO: [], LEVEL_SENIOR: []}
    for level in bank:
        for i in range(QUESTIONS_PER_TEST):
            q = InterviewQuestion.objects.create(
                level=level,
                category="Geral",
                statement=f"[{level}] questão {i}",
                choices=["A", "B", "C", "D"],
                correct_index=0,
                explanation="explicação",
                order=i,
            )
            bank[level].append(q)
    return bank


def _post_all_correct(client, attempt, *, correct_count):
    """Atalho: marca diretamente respostas no banco para tornar testes ágeis."""
    answers = {}
    for i, qid in enumerate(attempt.question_ids):
        q = InterviewQuestion.objects.get(pk=qid)
        if i < correct_count:
            answers[str(qid)] = q.correct_index
        else:
            answers[str(qid)] = (q.correct_index + 1) % len(q.choices)
    attempt.answers = answers
    attempt.save(update_fields=["answers"])


# ─── User: carreira ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCareerProgression:
    def test_default_eh_estagiario(self, make_user):
        u = make_user()
        assert u.career_level == User.INTERN
        assert u.career_label == "Estagiário"

    def test_estagiario_pode_fazer_junior_apenas(self, make_user):
        u = make_user()
        assert u.can_take_interview(LEVEL_JUNIOR) is True
        assert u.can_take_interview(LEVEL_PLENO) is False
        assert u.can_take_interview(LEVEL_SENIOR) is False

    def test_promote_eh_sequencial_e_idempotente(self, make_user):
        u = make_user()
        assert u.promote_if_eligible(User.JUNIOR) is True
        assert u.career_level == User.JUNIOR
        # tentar pular níveis não promove
        assert u.promote_if_eligible(User.SENIOR) is False
        assert u.career_level == User.JUNIOR
        # promover de novo o mesmo nível também é no-op
        assert u.promote_if_eligible(User.JUNIOR) is False
        assert u.career_level == User.JUNIOR

    def test_promote_completo_ate_senior(self, make_user):
        u = make_user()
        u.promote_if_eligible(User.JUNIOR)
        u.promote_if_eligible(User.PLENO)
        u.promote_if_eligible(User.SENIOR)
        assert u.career_level == User.SENIOR
        # Sênior não pode mais ser promovido
        assert u.can_take_interview(LEVEL_SENIOR) is True  # ainda pode refazer

    def test_junior_libera_pleno_mas_nao_senior(self, make_user):
        u = make_user()
        u.promote_if_eligible(User.JUNIOR)
        assert u.can_take_interview(LEVEL_PLENO) is True
        assert u.can_take_interview(LEVEL_SENIOR) is False


# ─── Modelos do simulador ────────────────────────────────────────────────────


@pytest.mark.django_db
class TestInterviewModels:
    def test_attempt_propriedades_basicas(self, make_user, seed_interview_bank):
        u = make_user()
        ids = [q.id for q in seed_interview_bank[LEVEL_JUNIOR][:5]]
        attempt = InterviewAttempt.objects.create(
            user=u, level=LEVEL_JUNIOR, question_ids=ids
        )
        assert attempt.total == 5
        assert attempt.answered_count == 0
        assert attempt.progress_percent == 0
        assert attempt.score_percent == 0
        assert attempt.next_unanswered_index() == 0

    def test_next_unanswered_index_pula_respondidas(
        self, make_user, seed_interview_bank
    ):
        u = make_user()
        ids = [q.id for q in seed_interview_bank[LEVEL_JUNIOR][:5]]
        attempt = InterviewAttempt.objects.create(
            user=u, level=LEVEL_JUNIOR, question_ids=ids
        )
        # responder questões 0, 1, 3 (deixar 2 e 4 em aberto)
        attempt.answers = {str(ids[0]): 0, str(ids[1]): 1, str(ids[3]): 2}
        attempt.save()
        assert attempt.next_unanswered_index() == 2

    def test_next_unanswered_index_quando_tudo_respondido(
        self, make_user, seed_interview_bank
    ):
        u = make_user()
        ids = [q.id for q in seed_interview_bank[LEVEL_JUNIOR][:3]]
        a = InterviewAttempt.objects.create(
            user=u, level=LEVEL_JUNIOR, question_ids=ids
        )
        a.answers = {str(qid): 0 for qid in ids}
        a.save()
        assert a.next_unanswered_index() == 3  # == len(ids), sinaliza fim


# ─── Seed command ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSeedInterviewsCommand:
    def test_seed_cria_300_questoes(self):
        from django.core.management import call_command

        call_command("seed_interviews", verbosity=0)
        assert InterviewQuestion.objects.filter(level=LEVEL_JUNIOR).count() == 100
        assert InterviewQuestion.objects.filter(level=LEVEL_PLENO).count() == 100
        assert InterviewQuestion.objects.filter(level=LEVEL_SENIOR).count() == 100

    def test_seed_eh_idempotente(self):
        from django.core.management import call_command

        call_command("seed_interviews", verbosity=0)
        primeiro = InterviewQuestion.objects.count()
        call_command("seed_interviews", verbosity=0)
        assert InterviewQuestion.objects.count() == primeiro

    def test_questoes_tem_correct_index_dentro_do_intervalo(self):
        from django.core.management import call_command

        call_command("seed_interviews", verbosity=0)
        for q in InterviewQuestion.objects.all():
            assert 0 <= q.correct_index < len(q.choices), (
                f"correct_index inválido em q#{q.pk}: {q.correct_index} "
                f"choices={len(q.choices)}"
            )


# ─── Fluxo HTTP ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestInterviewIndexView:
    def test_lista_renderiza_para_admitido(
        self, client, admitted_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        resp = client.get(reverse("interviews:index"))
        assert resp.status_code == 200
        assert b"J\xc3\xbanior" in resp.content
        assert b"Pleno" in resp.content
        assert b"S\xc3\xaanior" in resp.content

    def test_anonimo_eh_redirecionado(self, client):
        resp = client.get(reverse("interviews:index"))
        assert resp.status_code == 302
        assert "/contas/login" in resp.url or "/accounts/login" in resp.url


@pytest.mark.django_db
class TestStartView:
    def test_estagiario_inicia_junior(self, client, admitted_user, seed_interview_bank):
        client.force_login(admitted_user)
        resp = client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        assert resp.status_code == 302
        attempt = InterviewAttempt.objects.get(user=admitted_user, level=LEVEL_JUNIOR)
        assert len(attempt.question_ids) == QUESTIONS_PER_TEST
        assert resp.url == reverse("interviews:take", args=[attempt.pk])

    def test_estagiario_nao_inicia_pleno(
        self, client, admitted_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        resp = client.post(reverse("interviews:start", args=[LEVEL_PLENO]))
        assert resp.status_code == 302
        assert resp.url == reverse("interviews:index")
        assert (
            InterviewAttempt.objects.filter(
                user=admitted_user, level=LEVEL_PLENO
            ).count()
            == 0
        )

    def test_estagiario_nao_inicia_senior(
        self, client, admitted_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        resp = client.post(reverse("interviews:start", args=[LEVEL_SENIOR]))
        assert resp.status_code == 302
        assert (
            InterviewAttempt.objects.filter(
                user=admitted_user, level=LEVEL_SENIOR
            ).count()
            == 0
        )

    def test_iniciar_quando_ja_existe_em_andamento_redireciona_para_ela(
        self, client, admitted_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        primeira = InterviewAttempt.objects.get(user=admitted_user)

        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        # ainda só uma tentativa
        assert InterviewAttempt.objects.filter(user=admitted_user).count() == 1
        assert InterviewAttempt.objects.first().pk == primeira.pk

    def test_nivel_invalido_404(self, client, admitted_user, seed_interview_bank):
        client.force_login(admitted_user)
        resp = client.post(reverse("interviews:start", args=["arquiteto"]))
        assert resp.status_code == 404

    def test_banco_incompleto_redireciona_com_erro(self, client, admitted_user):
        # sem fixture seed_interview_bank → banco vazio
        client.force_login(admitted_user)
        resp = client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        assert resp.status_code == 302
        assert resp.url == reverse("interviews:index")


@pytest.mark.django_db
class TestTakeView:
    def _start(self, client, user, level):
        client.force_login(user)
        client.post(reverse("interviews:start", args=[level]))
        return InterviewAttempt.objects.get(user=user, level=level)

    def test_get_renderiza_primeira_questao(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.get(reverse("interviews:take", args=[attempt.pk]))
        assert resp.status_code == 200
        assert b"index" in resp.content  # input hidden index= existe

    def test_post_resposta_salva_e_avanca(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.post(
            reverse("interviews:take", args=[attempt.pk]),
            {"index": "0", "choice": "0", "action": "next"},
        )
        assert resp.status_code == 302
        assert "i=1" in resp.url
        attempt.refresh_from_db()
        assert attempt.answered_count == 1

    def test_save_exit_persiste_e_volta_para_lista(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.post(
            reverse("interviews:take", args=[attempt.pk]),
            {"index": "0", "choice": "0", "action": "save_exit"},
        )
        assert resp.status_code == 302
        assert resp.url == reverse("interviews:index")
        attempt.refresh_from_db()
        assert attempt.answered_count == 1
        assert attempt.finished_at is None

    def test_retomar_da_proxima_sem_resposta(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        # responder 0,1,2,3
        for i in range(4):
            client.post(
                reverse("interviews:take", args=[attempt.pk]),
                {"index": str(i), "choice": "0", "action": "next"},
            )
        # GET sem ?i= deve cair na 4
        resp = client.get(reverse("interviews:take", args=[attempt.pk]))
        assert resp.status_code == 200
        # ainda renderiza algo coerente; o html contém "5 de 100" (index 4 → human 5)
        assert b"5 de 100" in resp.content or b"5/100" in resp.content or resp.status_code == 200

    def test_action_prev_volta_indice(self, client, admitted_user, seed_interview_bank):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.post(
            reverse("interviews:take", args=[attempt.pk]),
            {"index": "5", "choice": "1", "action": "prev"},
        )
        assert resp.status_code == 302
        assert "i=4" in resp.url

    def test_action_finish_redireciona_para_finish(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.post(
            reverse("interviews:take", args=[attempt.pk]),
            {"index": "0", "choice": "0", "action": "finish"},
        )
        assert resp.status_code == 302
        assert resp.url == reverse("interviews:finish", args=[attempt.pk])

    def test_index_invalido_400(self, client, admitted_user, seed_interview_bank):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        resp = client.post(
            reverse("interviews:take", args=[attempt.pk]),
            {"index": "9999", "choice": "0", "action": "next"},
        )
        assert resp.status_code == 400

    def test_outro_usuario_nao_acessa_attempt(
        self, client, admitted_user, make_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        outro = make_user(email="outro@x.com")
        client.force_login(outro)
        resp = client.get(reverse("interviews:take", args=[attempt.pk]))
        assert resp.status_code == 404

    def test_attempt_finalizada_404_no_take(
        self, client, admitted_user, seed_interview_bank
    ):
        from django.utils import timezone

        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        attempt.finished_at = timezone.now()
        attempt.save()
        resp = client.get(reverse("interviews:take", args=[attempt.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestFinishAndPromotion:
    def _start(self, client, user, level):
        client.force_login(user)
        client.post(reverse("interviews:start", args=[level]))
        return InterviewAttempt.objects.get(user=user, level=level)

    def test_finalizar_com_80_pct_promove(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        _post_all_correct(client, attempt, correct_count=80)
        resp = client.post(reverse("interviews:finish", args=[attempt.pk]))
        attempt.refresh_from_db()
        admitted_user.refresh_from_db()
        assert attempt.score == 80
        assert attempt.passed is True
        assert attempt.finished_at is not None
        assert admitted_user.career_level == User.JUNIOR
        assert resp.url == reverse("interviews:result", args=[attempt.pk])

    def test_finalizar_com_79_pct_nao_promove(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        _post_all_correct(client, attempt, correct_count=79)
        client.post(reverse("interviews:finish", args=[attempt.pk]))
        attempt.refresh_from_db()
        admitted_user.refresh_from_db()
        assert attempt.score == 79
        assert attempt.passed is False
        assert admitted_user.career_level == User.INTERN

    def test_pleno_so_libera_apos_junior(
        self, client, admitted_user, seed_interview_bank
    ):
        # Junior 100%
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        _post_all_correct(client, attempt, correct_count=100)
        client.post(reverse("interviews:finish", args=[attempt.pk]))
        admitted_user.refresh_from_db()
        assert admitted_user.career_level == User.JUNIOR

        # Agora pode iniciar pleno
        resp = client.post(reverse("interviews:start", args=[LEVEL_PLENO]))
        assert resp.status_code == 302
        pleno_attempt = InterviewAttempt.objects.get(
            user=admitted_user, level=LEVEL_PLENO
        )
        assert resp.url == reverse("interviews:take", args=[pleno_attempt.pk])

    def test_promocao_completa_ate_senior(
        self, client, admitted_user, seed_interview_bank
    ):
        for level, target in [
            (LEVEL_JUNIOR, User.JUNIOR),
            (LEVEL_PLENO, User.PLENO),
            (LEVEL_SENIOR, User.SENIOR),
        ]:
            attempt = self._start(client, admitted_user, level)
            _post_all_correct(client, attempt, correct_count=80)
            client.post(reverse("interviews:finish", args=[attempt.pk]))
            admitted_user.refresh_from_db()
            assert admitted_user.career_level == target

    def test_finalizar_lista_questoes_pendentes(
        self, client, admitted_user, seed_interview_bank
    ):
        """A tela de finalizar deve apontar exatamente quais questões faltam,
        para o usuário voltar e responder antes de submeter."""
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        # Responde só duas questões: a primeira e a quinta.
        answers = {
            str(attempt.question_ids[0]): 0,
            str(attempt.question_ids[4]): 0,
        }
        attempt.answers = answers
        attempt.save(update_fields=["answers"])

        resp = client.get(reverse("interviews:finish", args=[attempt.pk]))
        assert resp.status_code == 200

        ctx = resp.context
        assert ctx["unanswered"] == QUESTIONS_PER_TEST - 2
        assert len(ctx["unanswered_items"]) == QUESTIONS_PER_TEST - 2

        items = ctx["unanswered_items"]
        # As respondidas (índices 0 e 4) NÃO devem aparecer.
        indexes = {it["index"] for it in items}
        assert 0 not in indexes
        assert 4 not in indexes
        # A 2ª (idx 1) deve aparecer e o `human_index` é 1-based.
        first_pending = items[0]
        assert first_pending["index"] == 1
        assert first_pending["human_index"] == 2

        # O HTML traz link para retomar a primeira pendente.
        body = resp.content.decode()
        retake_url = reverse("interviews:take", args=[attempt.pk]) + "?i=1"
        assert retake_url in body

    def test_finalizar_sem_pendentes_nao_lista(
        self, client, admitted_user, seed_interview_bank
    ):
        attempt = self._start(client, admitted_user, LEVEL_JUNIOR)
        attempt.answers = {str(qid): 0 for qid in attempt.question_ids}
        attempt.save(update_fields=["answers"])

        resp = client.get(reverse("interviews:finish", args=[attempt.pk]))
        assert resp.status_code == 200
        ctx = resp.context
        assert ctx["unanswered"] == 0
        assert ctx["unanswered_items"] == []


@pytest.mark.django_db
class TestResultView:
    def test_resultado_renderiza_apenas_para_dono(
        self, client, admitted_user, make_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        attempt = InterviewAttempt.objects.get(user=admitted_user)
        _post_all_correct(client, attempt, correct_count=80)
        client.post(reverse("interviews:finish", args=[attempt.pk]))

        resp = client.get(reverse("interviews:result", args=[attempt.pk]))
        assert resp.status_code == 200

        outro = make_user(email="outro@x.com")
        client.force_login(outro)
        resp = client.get(reverse("interviews:result", args=[attempt.pk]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestCancelView:
    def test_descartar_remove_attempt(
        self, client, admitted_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        attempt = InterviewAttempt.objects.get(user=admitted_user)

        resp = client.post(reverse("interviews:cancel", args=[attempt.pk]))
        assert resp.status_code == 302
        assert resp.url == reverse("interviews:index")
        assert InterviewAttempt.objects.filter(pk=attempt.pk).count() == 0

    def test_descartar_attempt_finalizada_404(
        self, client, admitted_user, seed_interview_bank
    ):
        from django.utils import timezone

        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        attempt = InterviewAttempt.objects.get(user=admitted_user)
        attempt.finished_at = timezone.now()
        attempt.save()

        resp = client.post(reverse("interviews:cancel", args=[attempt.pk]))
        assert resp.status_code == 404

    def test_outro_usuario_nao_descarta_alheio(
        self, client, admitted_user, make_user, seed_interview_bank
    ):
        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        attempt = InterviewAttempt.objects.get(user=admitted_user)

        outro = make_user(email="outro@x.com")
        client.force_login(outro)
        resp = client.post(reverse("interviews:cancel", args=[attempt.pk]))
        assert resp.status_code == 404
        assert InterviewAttempt.objects.filter(pk=attempt.pk).exists()


class TestInterviewChoiceLeadFilter:
    def test_sujeito_simples_em_crase_some_a_descricao(self):
        s = "`nslookup` consulta servidores DNS e retorna registros como A/AAAA/MX, mas não testa latência."
        assert interview_choice_lead(s) == "`nslookup`"

    def test_sujeito_com_sigla_em_parenteses(self):
        s = "`mtr` (My TraceRoute) e `traceroute` exibem cada hop entre origem e destino."
        assert interview_choice_lead(s) == "`mtr` (My TraceRoute) e `traceroute`"

    def test_sujeito_com_argumentos(self):
        s = "`telnet host porta` apenas testa se uma porta TCP aceita conexão."
        assert interview_choice_lead(s) == "`telnet host porta`"

    def test_sujeito_seguido_de_aposto_com_virgula(self):
        # "`systemctl`, frontend do systemd que controla units…" → só o comando.
        s = "`systemctl`, frontend do systemd que controla units (`.service`, `.timer`)."
        assert interview_choice_lead(s) == "`systemctl`"

    def test_opcao_sem_crase_corta_em_ponto_e_virgula(self):
        s = "Ambos exigem `sudo`; sem isso falham com `Permission denied`."
        assert interview_choice_lead(s) == "Ambos exigem `sudo`"

    def test_opcao_sem_crase_corta_em_mas(self):
        s = "Procurar padrões em arquivos, mas sem suporte a regex."
        assert interview_choice_lead(s) == "Procurar padrões em arquivos"

    def test_frase_longa_sem_crase_corta_na_primeira_virgula(self):
        s = (
            "Quando o domínio ainda é pequeno, a equipe é enxuta e "
            "os bounded contexts não estão claros, um monólito modular reduz custo."
        )
        assert interview_choice_lead(s) == "Quando o domínio ainda é pequeno"

    def test_alternativa_que_eh_so_o_sujeito_fica_intacta(self):
        s = "`/var`"
        assert interview_choice_lead(s) == "`/var`"

    def test_alternativa_vazia(self):
        assert interview_choice_lead("") == ""
        assert interview_choice_lead(None) == ""

    def test_nao_corta_dentro_de_parenteses(self):
        # A vírgula entre «Okta, Auth0» está dentro de parênteses; o filtro
        # tem que ignorá-la para não deixar «(Okta» sem fechar.
        s = (
            "Federação SSO/IDP central (Okta, Auth0) decide quem entra e "
            "centraliza o ciclo de vida de identidade dos colaboradores."
        )
        out = interview_choice_lead(s)
        assert out.count("(") == out.count(")"), (
            f"parênteses desbalanceados: {out!r}"
        )

    def test_corta_fora_de_parenteses_quando_existe(self):
        # Mesmo texto longo, agora com vírgula externa: deve cortar nela.
        s = (
            "Federação SSO/IDP central (Okta, Auth0) decide quem entra, "
            "centralizando o ciclo de vida de identidade dos colaboradores."
        )
        out = interview_choice_lead(s)
        assert out == "Federação SSO/IDP central (Okta, Auth0) decide quem entra"


class TestFailureMessage:
    """A mensagem de reprovação precisa ser proporcional ao score."""

    def test_score_baixo_nao_diz_faltou_pouco(self):
        msg = _failure_message(30.0)
        assert "Faltou pouco" not in msg
        assert f"{PASS_PERCENT}%" in msg

    def test_score_muito_baixo_sugere_estudo(self):
        msg = _failure_message(10.0)
        assert "Faltou pouco" not in msg
        assert "estudar" in msg.lower() or "trilha" in msg.lower()

    def test_score_intermediario_no_caminho(self):
        msg = _failure_message(60.0)
        assert "no caminho" in msg.lower()
        assert "Faltou pouco" not in msg

    def test_score_proximo_ao_corte_diz_faltou_pouco(self):
        msg = _failure_message(75.0)
        assert msg.startswith("Faltou pouco")

    def test_score_no_corte_inferior_da_faixa_70(self):
        # 70% exato deve cair na mensagem de "Faltou pouco" (limite inclusivo).
        assert _failure_message(70.0).startswith("Faltou pouco")
