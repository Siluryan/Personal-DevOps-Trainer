"""Simulador de entrevistas: lista, sessão de prova e resultado.

Fluxo:
1. `IndexView` mostra os 3 níveis com status (bloqueado / disponível / em andamento / concluído).
2. `StartView` (POST) cria nova tentativa ou retoma a em andamento.
3. `TakeView` exibe e processa uma questão por vez; cada POST salva a resposta.
4. `FinishView` (POST) calcula score final e promove o usuário se ≥ 80%.
5. `ResultView` mostra gabarito.
"""
from __future__ import annotations

import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

from apps.accounts.models import User as UserModel  # for type-only / nivel mapping

from .models import (
    LEVEL_CHOICES,
    LEVEL_JUNIOR,
    LEVEL_PLENO,
    LEVEL_SENIOR,
    PASS_PERCENT,
    QUESTIONS_PER_TEST,
    InterviewAttempt,
    InterviewQuestion,
)

# ─── Mapeamento entre nível da entrevista e nível anterior do User ───────────
LEVEL_TO_USER_PREV = {
    LEVEL_JUNIOR: UserModel.INTERN,
    LEVEL_PLENO: UserModel.JUNIOR,
    LEVEL_SENIOR: UserModel.PLENO,
}
LEVEL_TO_USER_TARGET = {
    LEVEL_JUNIOR: UserModel.JUNIOR,
    LEVEL_PLENO: UserModel.PLENO,
    LEVEL_SENIOR: UserModel.SENIOR,
}


def _failure_message(score_percent: float) -> str:
    """Mensagem de reprovação proporcional ao acerto.

    «Faltou pouco» só aparece quando faz sentido (≥ 70%); resultados mais baixos
    recebem um texto que reflete o trabalho real que ainda falta.
    """
    rule = f"São necessários {PASS_PERCENT}% para subir de nível."
    if score_percent >= 70:
        return f"Faltou pouco. {rule} Revise o gabarito e tente de novo."
    if score_percent >= 50:
        return (
            f"Você está no caminho, mas ainda não passou. {rule} "
            "Estude os pontos onde errou no gabarito antes de refazer."
        )
    if score_percent >= 30:
        return (
            f"Ainda há terreno a cobrir. {rule} "
            "Use o gabarito como guia de estudos antes de tentar de novo."
        )
    return (
        f"O resultado mostra que vale estudar o conteúdo antes de refazer. {rule} "
        "Comece pelo gabarito e pelos tópicos relacionados na trilha."
    )


def _level_status(user, level: str) -> dict:
    """Resume o status de um nível para o usuário."""
    target = LEVEL_TO_USER_TARGET[level]
    unlocked = user.can_take_interview(level)
    last = (
        user.interview_attempts.filter(level=level).order_by("-started_at").first()
    )
    in_progress = (
        user.interview_attempts.filter(level=level, finished_at__isnull=True)
        .order_by("-started_at")
        .first()
    )
    achieved = user.career_level == target or (
        UserModel.CAREER_ORDER.index(user.career_level)
        > UserModel.CAREER_ORDER.index(target)
    )
    return {
        "level": level,
        "unlocked": unlocked,
        "achieved": achieved,
        "in_progress": in_progress,
        "last": last,
    }


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "interviews/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["levels"] = [
            {
                "key": LEVEL_JUNIOR,
                "label": "Júnior",
                "description": (
                    "Fundamentos: Linux, redes, Docker, Git, CI/CD, cloud "
                    "e segurança básica."
                ),
                "status": _level_status(user, LEVEL_JUNIOR),
            },
            {
                "key": LEVEL_PLENO,
                "label": "Pleno",
                "description": (
                    "Operação real: Kubernetes, IaC, observability, "
                    "DevSecOps, troubleshooting e performance."
                ),
                "status": _level_status(user, LEVEL_PLENO),
            },
            {
                "key": LEVEL_SENIOR,
                "label": "Sênior",
                "description": (
                    "Arquitetura: trade-offs, escalabilidade, multi-region, "
                    "SRE, segurança avançada e liderança técnica."
                ),
                "status": _level_status(user, LEVEL_SENIOR),
            },
        ]
        ctx["pass_percent"] = PASS_PERCENT
        ctx["questions_total"] = QUESTIONS_PER_TEST
        ctx["career_label"] = user.career_label
        return ctx


class StartView(LoginRequiredMixin, View):
    """Cria nova tentativa ou redireciona para a em andamento."""

    def post(self, request, level):
        if level not in dict(LEVEL_CHOICES):
            raise Http404("Nível inválido.")

        user = request.user
        if not user.can_take_interview(level):
            messages.warning(
                request,
                "Você ainda não desbloqueou esse nível. Conclua o anterior com 80%+.",
            )
            return redirect("interviews:index")

        in_progress = (
            user.interview_attempts.filter(level=level, finished_at__isnull=True)
            .order_by("-started_at")
            .first()
        )
        if in_progress:
            in_progress.refresh_from_db()
            n = len(in_progress.question_ids)
            if n == 0:
                return redirect("interviews:take", pk=in_progress.pk)
            ri = in_progress.resume_index()
            if ri >= n:
                return redirect("interviews:finish", pk=in_progress.pk)
            return redirect(
                reverse("interviews:take", args=[in_progress.pk]) + f"?i={ri}"
            )

        ids = list(
            InterviewQuestion.objects.filter(level=level, is_active=True).values_list(
                "id", flat=True
            )
        )
        if len(ids) < QUESTIONS_PER_TEST:
            messages.error(
                request,
                f"Banco de questões incompleto para {level} "
                f"({len(ids)}/{QUESTIONS_PER_TEST}). Avise o admin.",
            )
            return redirect("interviews:index")

        random.shuffle(ids)
        ids = ids[:QUESTIONS_PER_TEST]

        attempt = InterviewAttempt.objects.create(
            user=user, level=level, question_ids=ids
        )
        return redirect(
            reverse("interviews:take", args=[attempt.pk]) + "?i=0"
        )


class TakeView(LoginRequiredMixin, View):
    """Mostra a próxima questão sem resposta. POST salva a resposta atual."""

    template_name = "interviews/take.html"

    def _get_attempt(self, request, pk: int) -> InterviewAttempt:
        attempt = get_object_or_404(
            InterviewAttempt, pk=pk, user=request.user, finished_at__isnull=True
        )
        return attempt

    def _build_context(self, attempt: InterviewAttempt, idx: int):
        if idx >= len(attempt.question_ids):
            return None
        qid = attempt.question_ids[idx]
        try:
            question = InterviewQuestion.objects.get(pk=qid)
        except InterviewQuestion.DoesNotExist:
            return None
        total = len(attempt.question_ids)
        return {
            "attempt": attempt,
            "question": question,
            "index": idx,
            "human_index": idx + 1,
            "total": total,
            "progress_percent": int(
                round(100 * attempt.answered_count / max(total, 1))
            ),
            "answered_count": attempt.answered_count,
            "previous_choice": (attempt.answers or {}).get(str(qid)),
            "level_label": attempt.get_level_display(),
        }

    def get(self, request, pk):
        attempt = self._get_attempt(request, pk)
        idx_param = request.GET.get("i")
        if idx_param is not None:
            try:
                idx = int(idx_param)
                if not 0 <= idx < len(attempt.question_ids):
                    raise ValueError
            except ValueError:
                return HttpResponseBadRequest("índice inválido")
        else:
            idx = attempt.resume_index()
            if idx >= len(attempt.question_ids):
                return redirect("interviews:finish", pk=attempt.pk)
        ctx = self._build_context(attempt, idx)
        if not ctx:
            return redirect("interviews:finish", pk=attempt.pk)
        if attempt.last_question_index != idx:
            attempt.last_question_index = idx
            attempt.save(update_fields=["last_question_index"])
        from django.shortcuts import render

        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        attempt = self._get_attempt(request, pk)
        try:
            idx = int(request.POST["index"])
        except (KeyError, ValueError):
            return HttpResponseBadRequest("index ausente")
        if not 0 <= idx < len(attempt.question_ids):
            return HttpResponseBadRequest("index fora do intervalo")

        action = request.POST.get("action", "next")
        choice_raw = request.POST.get("choice", "").strip()

        qid = attempt.question_ids[idx]
        update_fields: list[str] = ["last_question_index"]
        attempt.last_question_index = idx
        if choice_raw != "":
            try:
                choice_idx = int(choice_raw)
            except ValueError:
                return HttpResponseBadRequest("choice inválida")
            answers = {str(k): v for k, v in (attempt.answers or {}).items()}
            answers[str(qid)] = choice_idx
            attempt.answers = answers
            update_fields.insert(0, "answers")

        attempt.save(update_fields=update_fields)

        if action == "save_exit":
            messages.info(
                request,
                "Progresso salvo. Você pode retomar a qualquer momento.",
            )
            return redirect("interviews:index")
        if action == "prev":
            new_idx = max(0, idx - 1)
            return redirect(reverse("interviews:take", args=[attempt.pk]) + f"?i={new_idx}")
        if action == "finish":
            return redirect("interviews:finish", pk=attempt.pk)

        new_idx = idx + 1
        if new_idx >= len(attempt.question_ids):
            return redirect("interviews:finish", pk=attempt.pk)
        return redirect(reverse("interviews:take", args=[attempt.pk]) + f"?i={new_idx}")


class FinishView(LoginRequiredMixin, View):
    """Calcula score, marca como concluído e promove o usuário se passar."""

    template_name = "interviews/finish_confirm.html"

    def _get_attempt(self, request, pk):
        return get_object_or_404(
            InterviewAttempt, pk=pk, user=request.user, finished_at__isnull=True
        )

    def get(self, request, pk):
        from django.shortcuts import render

        attempt = self._get_attempt(request, pk)
        answered_keys = {str(k) for k in (attempt.answers or {}).keys()}
        unanswered_items = [
            {"index": i, "human_index": i + 1}
            for i, qid in enumerate(attempt.question_ids)
            if str(qid) not in answered_keys
        ]
        return render(
            request,
            self.template_name,
            {
                "attempt": attempt,
                "unanswered": len(unanswered_items),
                "unanswered_items": unanswered_items,
                "total": len(attempt.question_ids),
                "level_label": attempt.get_level_display(),
            },
        )

    def post(self, request, pk):
        attempt = self._get_attempt(request, pk)
        questions = {
            q.id: q
            for q in InterviewQuestion.objects.filter(id__in=attempt.question_ids)
        }
        score = 0
        for qid in attempt.question_ids:
            q = questions.get(qid)
            if not q:
                continue
            picked = (attempt.answers or {}).get(str(qid))
            if picked is not None and int(picked) == q.correct_index:
                score += 1

        attempt.score = score
        attempt.passed = (score / max(len(attempt.question_ids), 1)) * 100 >= PASS_PERCENT
        attempt.finished_at = timezone.now()
        attempt.save()

        if attempt.passed:
            promoted = request.user.promote_if_eligible(LEVEL_TO_USER_TARGET[attempt.level])
            if promoted:
                messages.success(
                    request,
                    f"Parabéns! Você foi promovido para {request.user.career_label}.",
                )
            else:
                messages.success(
                    request,
                    "Você passou no teste. Continue praticando ou avance para o próximo nível.",
                )
        else:
            score_percent = (score / max(len(attempt.question_ids), 1)) * 100
            messages.warning(request, _failure_message(score_percent))

        return redirect("interviews:result", pk=attempt.pk)


class ResultView(LoginRequiredMixin, TemplateView):
    template_name = "interviews/result.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = get_object_or_404(
            InterviewAttempt, pk=kwargs["pk"], user=self.request.user
        )
        if not attempt.finished_at:
            return ctx
        questions = {
            q.id: q
            for q in InterviewQuestion.objects.filter(id__in=attempt.question_ids)
        }
        rows = []
        for qid in attempt.question_ids:
            q = questions.get(qid)
            if not q:
                continue
            picked = (attempt.answers or {}).get(str(qid))
            picked_idx = int(picked) if picked is not None else None
            rows.append(
                {
                    "question": q,
                    "picked_idx": picked_idx,
                    "is_correct": (picked_idx is not None and picked_idx == q.correct_index),
                }
            )
        ctx["attempt"] = attempt
        ctx["rows"] = rows
        ctx["correct_count"] = attempt.score
        ctx["total"] = len(attempt.question_ids)
        ctx["score_percent"] = attempt.score_percent
        ctx["pass_percent"] = PASS_PERCENT
        ctx["level_label"] = attempt.get_level_display()
        if not attempt.passed:
            ctx["failure_message"] = _failure_message(attempt.score_percent)
        return ctx


class CancelView(LoginRequiredMixin, View):
    """Permite descartar uma tentativa em andamento (começa do zero)."""

    def post(self, request, pk):
        attempt = get_object_or_404(
            InterviewAttempt, pk=pk, user=request.user, finished_at__isnull=True
        )
        attempt.delete()
        messages.info(request, "Tentativa descartada.")
        return redirect("interviews:index")
