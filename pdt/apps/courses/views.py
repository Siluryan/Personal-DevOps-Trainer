"""Views da trilha: lista de tópicos, detalhe, quiz e resultado."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.gamification.models import LabCompletion, TopicAttempt, TopicAttemptAnswer, TopicScore

from .models import Choice, Lab, Phase, Question, Topic


class TrackView(LoginRequiredMixin, TemplateView):
    template_name = "courses/track.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["phases"] = Phase.objects.prefetch_related(
            "topics", "topics__materials"
        ).all()
        scores = {
            s.topic_id: s
            for s in TopicScore.objects.filter(user=self.request.user)
        }
        ctx["scores"] = scores
        return ctx


class TopicDetailView(LoginRequiredMixin, DetailView):
    model = Topic
    template_name = "courses/topic_detail.html"
    slug_url_kwarg = "slug"
    context_object_name = "topic"

    def get_queryset(self):
        return Topic.objects.select_related("phase", "lesson").prefetch_related(
            "materials", "labs"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["score"] = TopicScore.objects.filter(
            user=self.request.user, topic=self.object
        ).first()
        ctx["recent_attempts"] = TopicAttempt.objects.filter(
            user=self.request.user, topic=self.object
        )[:5]
        labs = list(self.object.labs.filter(is_active=True))
        completed_ids = set(
            LabCompletion.objects.filter(
                user=self.request.user, lab__topic=self.object
            ).values_list("lab_id", flat=True)
        )
        for lab in labs:
            lab.elid = f"lab-spec-{lab.id}"
            lab.is_done = lab.id in completed_ids
        ctx["labs"] = labs
        return ctx


class QuizView(LoginRequiredMixin, TemplateView):
    template_name = "courses/quiz.html"

    def _get_topic(self, slug):
        return get_object_or_404(Topic, slug=slug)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topic = self._get_topic(kwargs["slug"])
        questions = list(
            topic.questions.filter(is_active=True).prefetch_related("choices")[:10]
        )
        ctx["topic"] = topic
        ctx["questions"] = questions
        return ctx

    def post(self, request, slug):
        topic = self._get_topic(slug)
        questions = list(topic.questions.filter(is_active=True).prefetch_related("choices")[:10])
        if not questions:
            messages.warning(request, "Este tópico ainda não tem questões cadastradas.")
            return redirect("courses:topic_detail", slug=slug)

        attempt = TopicAttempt.objects.create(
            user=request.user, topic=topic, total_questions=len(questions)
        )
        score = 0
        for question in questions:
            picked = request.POST.get(f"q_{question.id}")
            choice: Choice | None = None
            correct = False
            if picked:
                try:
                    choice = Choice.objects.filter(
                        id=int(picked), question=question
                    ).first()
                except (ValueError, TypeError):
                    choice = None
                if choice and choice.is_correct:
                    correct = True
                    score += 1
            TopicAttemptAnswer.objects.create(
                attempt=attempt,
                question=question,
                choice=choice,
                choice_text=choice.text if choice else "",
                is_correct=correct,
            )
        attempt.score = score
        attempt.finished_at = timezone.now()
        attempt.save()

        TopicScore.update_from_attempt(attempt)

        return redirect("courses:quiz_result", slug=slug, attempt_id=attempt.id)


class QuizResultView(LoginRequiredMixin, TemplateView):
    template_name = "courses/quiz_result.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topic = get_object_or_404(Topic, slug=kwargs["slug"])
        attempt = get_object_or_404(
            TopicAttempt, id=kwargs["attempt_id"], user=self.request.user, topic=topic
        )
        ctx["topic"] = topic
        ctx["attempt"] = attempt
        ctx["answers"] = attempt.answers.select_related("question", "choice").all()
        return ctx


class LabCompleteView(LoginRequiredMixin, View):
    """Registra a conclusão de um lab e resincroniza o bônus do tópico.

    POST simples (fetch do Alpine.js), não HTMX: a interação do lab inteira
    é client-side (monta comando, ordena passo, etc.); isso só persiste o
    resultado final quando o aluno acerta. Idempotente — refazer não soma
    ponto de novo, `TopicScore.sync_lab_bonus` recomputa do zero.
    """

    def post(self, request, lab_id):
        lab = get_object_or_404(Lab, id=lab_id, is_active=True)
        LabCompletion.objects.get_or_create(user=request.user, lab=lab)
        score = TopicScore.sync_lab_bonus(user=request.user, topic=lab.topic)
        return JsonResponse({"points": score.points, "lab_bonus": score.lab_bonus})
