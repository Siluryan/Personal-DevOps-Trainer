"""Carrega as 6 fases e 60 tópicos no banco. Idempotente."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.courses.models import Choice, Lesson, Material, Phase, Question, Topic
from apps.courses.seed_data import PHASES


class Command(BaseCommand):
    help = "Cria/atualiza fases, tópicos, aulas, materiais e questões da trilha."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-questions",
            action="store_true",
            help="Apaga e recria questões e materiais antes de inserir (não toca em respostas dos usuários).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        reset = opts["reset_questions"]
        for phase_index, phase_data in enumerate(PHASES, start=1):
            phase, _ = Phase.objects.update_or_create(
                order=phase_index,
                defaults={
                    "name": phase_data["name"],
                    "description": phase_data.get("description", ""),
                    "slug": slugify(phase_data["name"])[:140],
                },
            )
            self.stdout.write(self.style.SUCCESS(f"\n== {phase} =="))

            for topic_order, topic_data in enumerate(phase_data["topics"], start=1):
                topic, _ = Topic.objects.update_or_create(
                    phase=phase,
                    order=topic_order,
                    defaults={
                        "title": topic_data["title"],
                        "summary": topic_data.get("summary", ""),
                        "slug": slugify(topic_data["title"])[:200],
                    },
                )
                self.stdout.write(f"  - {topic_order:02d}. {topic.title}")

                lesson_data = topic_data.get("lesson", {}) or {}
                Lesson.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "intro": lesson_data.get("intro", ""),
                        "body": lesson_data.get("body", ""),
                        "practical": lesson_data.get("practical", ""),
                    },
                )

                if reset:
                    topic.materials.all().delete()
                    topic.questions.all().delete()

                for i, mat in enumerate(topic_data.get("materials", [])):
                    Material.objects.update_or_create(
                        topic=topic,
                        url=mat["url"],
                        defaults={
                            "title": mat.get("title", "")[:255],
                            "kind": mat.get("kind", "article"),
                            "description": mat.get("description", ""),
                            "language": mat.get("language", "pt-br"),
                            "order": i,
                        },
                    )

                for i, qd in enumerate(topic_data.get("questions", [])):
                    question, _ = Question.objects.update_or_create(
                        topic=topic,
                        order=i,
                        defaults={
                            "statement": qd["statement"],
                            "explanation": qd.get("explanation", ""),
                            "is_active": True,
                        },
                    )
                    question.choices.all().delete()
                    for ci, choice in enumerate(qd.get("choices", [])):
                        Choice.objects.create(
                            question=question,
                            text=choice["text"][:255],
                            is_correct=bool(choice.get("correct", False)),
                            order=ci,
                        )

        self.stdout.write(self.style.SUCCESS("\nSeed concluído."))
