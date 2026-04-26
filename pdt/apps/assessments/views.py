"""Fluxo do teste de admissão.

Fluxo completo:
1. `StartView` apresenta as regras e cria uma `AdmissionAttempt` ao iniciar.
2. `TakeView` exibe e processa as 10 questões em uma única página.
3. `ResultView` mostra acerto/erro e libera (ou bloqueia) a plataforma.
4. `RetakeView` permite tentar de novo após reprovação.
"""
from __future__ import annotations

import random
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View

from .models import AdmissionAttempt, AdmissionChoice, AdmissionQuestion

QUESTIONS_PER_TEST = 10
RETAKE_COOLDOWN = timedelta(hours=12)


def _build_question_set() -> list[int]:
    """Sorteia 5 de Linux e 5 de Redes para totalizar 10."""
    linux_ids = list(
        AdmissionQuestion.objects.filter(area=AdmissionQuestion.LINUX, is_active=True).values_list("id", flat=True)
    )
    network_ids = list(
        AdmissionQuestion.objects.filter(area=AdmissionQuestion.NETWORK, is_active=True).values_list("id", flat=True)
    )
    random.shuffle(linux_ids)
    random.shuffle(network_ids)
    selected = linux_ids[:5] + network_ids[:5]
    random.shuffle(selected)
    return selected


class StartView(LoginRequiredMixin, TemplateView):
    template_name = "assessments/start.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pass_score"] = settings.ADMISSION_PASS_SCORE
        ctx["questions_total"] = QUESTIONS_PER_TEST
        last = self.request.user.admission_attempts.first()
        if last and not last.passed and last.finished_at:
            ctx["last_attempt"] = last
            ctx["next_try_at"] = last.finished_at + RETAKE_COOLDOWN
            ctx["can_retake"] = timezone.now() >= ctx["next_try_at"]
        else:
            ctx["can_retake"] = True
        return ctx

    def post(self, request, *args, **kwargs):
        if request.user.admission_passed:
            return redirect("core:dashboard")

        last = request.user.admission_attempts.first()
        if (
            last
            and not last.passed
            and last.finished_at
            and timezone.now() < last.finished_at + RETAKE_COOLDOWN
        ):
            messages.warning(
                request,
                "Você precisa aguardar antes de tentar novamente. "
                "Aproveite para revisar Linux e redes.",
            )
            return redirect("assessments:start")

        question_ids = _build_question_set()
        if len(question_ids) < QUESTIONS_PER_TEST:
            messages.error(request, "Banco de questões incompleto. Avise o administrador.")
            return redirect("core:landing")

        attempt = AdmissionAttempt.objects.create(
            user=request.user, question_ids=question_ids
        )
        return redirect("assessments:take")


class TakeView(LoginRequiredMixin, TemplateView):
    template_name = "assessments/take.html"

    def _current_attempt(self, request) -> AdmissionAttempt | None:
        return (
            AdmissionAttempt.objects.filter(user=request.user, finished_at__isnull=True)
            .order_by("-started_at")
            .first()
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = self._current_attempt(self.request)
        if not attempt:
            ctx["attempt"] = None
            return ctx
        questions = list(
            AdmissionQuestion.objects.filter(id__in=attempt.question_ids).prefetch_related("choices")
        )
        questions.sort(key=lambda q: attempt.question_ids.index(q.id))
        ctx["attempt"] = attempt
        ctx["questions"] = questions
        return ctx

    def get(self, request, *args, **kwargs):
        attempt = self._current_attempt(request)
        if not attempt:
            return redirect("assessments:start")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        attempt = self._current_attempt(request)
        if not attempt:
            return redirect("assessments:start")

        questions = AdmissionQuestion.objects.filter(id__in=attempt.question_ids).prefetch_related(
            "choices"
        )
        score = 0
        answers: dict[str, int] = {}
        for question in questions:
            picked = request.POST.get(f"q_{question.id}")
            if not picked:
                continue
            try:
                choice_id = int(picked)
            except (TypeError, ValueError):
                continue
            answers[str(question.id)] = choice_id
            if AdmissionChoice.objects.filter(
                id=choice_id, question=question, is_correct=True
            ).exists():
                score += 1

        attempt.score = score
        attempt.answers = answers
        attempt.passed = score >= settings.ADMISSION_PASS_SCORE
        attempt.finished_at = timezone.now()
        attempt.save()

        if attempt.passed:
            user = request.user
            user.admission_passed = True
            user.admission_score = score
            user.save(update_fields=["admission_passed", "admission_score"])
            messages.success(request, "Você foi aprovado. Bem-vindo(a) ao PDT!")
        else:
            messages.error(
                request,
                "Desempenho insuficiente. Reforce Linux e redes e tente novamente em algumas horas.",
            )

        return redirect("assessments:result", pk=attempt.pk)


class ResultView(LoginRequiredMixin, TemplateView):
    template_name = "assessments/result.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = get_object_or_404(
            AdmissionAttempt, pk=kwargs["pk"], user=self.request.user
        )
        ctx["attempt"] = attempt
        ctx["pass_score"] = settings.ADMISSION_PASS_SCORE
        ctx["next_try_at"] = (
            attempt.finished_at + RETAKE_COOLDOWN if attempt.finished_at else None
        )
        return ctx


class RetakeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        return redirect(reverse("assessments:start"))

    def get(self, request, *args, **kwargs):
        return redirect(reverse("assessments:start"))
