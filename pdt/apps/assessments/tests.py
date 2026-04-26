"""Testes do fluxo completo do teste de admissão."""
from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.assessments.models import (
    AdmissionAttempt,
    AdmissionChoice,
    AdmissionQuestion,
)


def _create_question(area: str, statement: str, correct_text: str, wrong_texts: list[str]):
    q = AdmissionQuestion.objects.create(area=area, statement=statement)
    AdmissionChoice.objects.create(question=q, text=correct_text, is_correct=True, order=0)
    for i, w in enumerate(wrong_texts, start=1):
        AdmissionChoice.objects.create(question=q, text=w, is_correct=False, order=i)
    return q


@pytest.fixture
def admission_bank(db):
    """Cria 6 questões de Linux + 6 de Redes (mais que o mínimo de 5+5)."""
    linux = []
    for i in range(6):
        linux.append(
            _create_question(
                AdmissionQuestion.LINUX,
                f"Linux Q{i}",
                f"linux-correta-{i}",
                ["a", "b", "c"],
            )
        )
    network = []
    for i in range(6):
        network.append(
            _create_question(
                AdmissionQuestion.NETWORK,
                f"Network Q{i}",
                f"network-correta-{i}",
                ["a", "b", "c"],
            )
        )
    return {"linux": linux, "network": network}


@pytest.mark.django_db
class TestAdmissionFlow:
    """Fluxo completo: start → take → result com score."""

    def test_start_requer_login(self, client):
        resp = client.get(reverse("assessments:start"))
        assert resp.status_code == 302

    def test_start_get_renderiza_para_pending_user(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        resp = client.get(reverse("assessments:start"))
        assert resp.status_code == 200

    def test_start_post_cria_attempt_e_redireciona(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        resp = client.post(reverse("assessments:start"))
        assert resp.status_code == 302
        assert resp.url == reverse("assessments:take")
        attempt = AdmissionAttempt.objects.get(user=pending_user)
        assert len(attempt.question_ids) == 10
        assert attempt.finished_at is None

    def test_start_post_falha_se_banco_incompleto(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.post(reverse("assessments:start"), follow=True)
        assert AdmissionAttempt.objects.count() == 0

    def test_take_redireciona_se_nao_houver_attempt(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.get(reverse("assessments:take"))
        assert resp.status_code == 302
        assert resp.url == reverse("assessments:start")

    def test_aprovacao_marca_admission_passed(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)

        post_data = {}
        for qid in attempt.question_ids:
            correct = AdmissionChoice.objects.get(question_id=qid, is_correct=True)
            post_data[f"q_{qid}"] = correct.id

        resp = client.post(reverse("assessments:take"), post_data)
        assert resp.status_code == 302
        attempt.refresh_from_db()
        pending_user.refresh_from_db()

        assert attempt.score == 10
        assert attempt.passed is True
        assert pending_user.admission_passed is True
        assert pending_user.admission_score == 10

    def test_reprovacao_nao_marca_admission_passed(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)

        post_data = {}
        for qid in attempt.question_ids:
            wrong = AdmissionChoice.objects.filter(question_id=qid, is_correct=False).first()
            post_data[f"q_{qid}"] = wrong.id

        client.post(reverse("assessments:take"), post_data)
        attempt.refresh_from_db()
        pending_user.refresh_from_db()

        assert attempt.score == 0
        assert attempt.passed is False
        assert pending_user.admission_passed is False

    def test_score_no_limite_aprova(self, client, pending_user, admission_bank):
        """5 acertos é exatamente o mínimo (ADMISSION_PASS_SCORE=5)."""
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)

        post_data = {}
        for i, qid in enumerate(attempt.question_ids):
            if i < 5:
                ch = AdmissionChoice.objects.get(question_id=qid, is_correct=True)
            else:
                ch = AdmissionChoice.objects.filter(
                    question_id=qid, is_correct=False
                ).first()
            post_data[f"q_{qid}"] = ch.id

        client.post(reverse("assessments:take"), post_data)
        attempt.refresh_from_db()
        pending_user.refresh_from_db()
        assert attempt.score == 5
        assert attempt.passed is True
        assert pending_user.admission_passed is True

    def test_cooldown_bloqueia_retry_imediato(self, client, pending_user, admission_bank):
        """Após reprovar, o usuário precisa esperar antes de tentar de novo."""
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)
        attempt.passed = False
        attempt.score = 0
        attempt.finished_at = timezone.now()
        attempt.save()

        resp = client.post(reverse("assessments:start"))
        assert resp.status_code == 302
        assert AdmissionAttempt.objects.filter(user=pending_user).count() == 1

    def test_retry_apos_cooldown(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)
        attempt.passed = False
        attempt.score = 0
        attempt.finished_at = timezone.now() - timedelta(hours=13)
        attempt.save()

        resp = client.post(reverse("assessments:start"))
        assert resp.status_code == 302
        assert resp.url == reverse("assessments:take")
        assert AdmissionAttempt.objects.filter(user=pending_user).count() == 2

    def test_resposta_em_branco_nao_pontua(self, client, pending_user, admission_bank):
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)

        client.post(reverse("assessments:take"), {})
        attempt.refresh_from_db()
        assert attempt.score == 0
        assert attempt.passed is False

    def test_take_post_fora_de_attempt_redireciona(self, client, pending_user):
        client.force_login(pending_user)
        resp = client.post(reverse("assessments:take"), {})
        assert resp.status_code == 302

    def test_5_linux_5_redes_garantido(self, client, pending_user, admission_bank):
        """Cada execução do teste sorteia 5 Linux + 5 Redes."""
        client.force_login(pending_user)
        client.post(reverse("assessments:start"))
        attempt = AdmissionAttempt.objects.get(user=pending_user)
        questions = AdmissionQuestion.objects.filter(id__in=attempt.question_ids)
        linux_count = questions.filter(area=AdmissionQuestion.LINUX).count()
        net_count = questions.filter(area=AdmissionQuestion.NETWORK).count()
        assert linux_count == 5
        assert net_count == 5
