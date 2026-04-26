"""Views da trilha: lista de tópicos, detalhe, quiz e resultado."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, TemplateView

from apps.gamification.models import TopicAttempt, TopicAttemptAnswer, TopicScore

from .models import Choice, Phase, Question, Topic


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
        return Topic.objects.select_related("phase", "lesson").prefetch_related("materials")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["score"] = TopicScore.objects.filter(
            user=self.request.user, topic=self.object
        ).first()
        ctx["recent_attempts"] = TopicAttempt.objects.filter(
            user=self.request.user, topic=self.object
        )[:5]
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
