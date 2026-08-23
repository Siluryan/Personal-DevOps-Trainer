"""Carrega as 6 fases e 60 tópicos no banco. Idempotente e não-destrutivo.

Aulas e questões editadas pelo admin (`seed_managed=False`) são preservadas:
o seed atualiza o registro na primeira vez que o encontra e, a partir do
momento em que alguém salva aquele registro pelo admin, para de tocá-lo. Use
`--force` para reverter uma edição e voltar a sincronizar com os arquivos de
`seed_data/`.

Fases, tópicos e materiais continuam totalmente sincronizados com o arquivo
fonte — só aula e questão têm conteúdo longo o suficiente para valer a pena
editar fora do git, e são as únicas que a reclamação original ("não consigo
alterar as questões e respostas por mim mesmo") mirava.
"""
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
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Sobrescreve também aulas e questões editadas pelo admin "
                "(seed_managed=False), voltando a marcá-las como sincronizadas."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        reset = opts["reset_questions"]
        force = opts["force"]
        preservadas = 0

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
                lesson, lesson_created = Lesson.objects.get_or_create(
                    topic=topic,
                    defaults={
                        "intro": lesson_data.get("intro", ""),
                        "body": lesson_data.get("body", ""),
                        "practical": lesson_data.get("practical", ""),
                        "seed_managed": True,
                    },
                )
                if not lesson_created:
                    if lesson.seed_managed or force:
                        lesson.intro = lesson_data.get("intro", "")
                        lesson.body = lesson_data.get("body", "")
                        lesson.practical = lesson_data.get("practical", "")
                        lesson.seed_managed = True
                        lesson.save(update_fields=["intro", "body", "practical", "seed_managed"])
                    else:
                        preservadas += 1
                        self.stdout.write(
                            "    (aula editada pelo admin, preservada — use --force para sobrescrever)"
                        )

                if reset:
                    topic.materials.all().delete()
                    # `--reset-questions` sempre foi para apagar tudo de propósito;
                    # aqui isso já implica --force para as questões deste tópico.
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
                    question, question_created = Question.objects.get_or_create(
                        topic=topic,
                        order=i,
                        defaults={
                            "statement": qd["statement"],
                            "explanation": qd.get("explanation", ""),
                            "is_active": True,
                            "seed_managed": True,
                        },
                    )
                    if question_created:
                        self._write_choices(question, qd.get("choices", []))
                        continue

                    if not question.seed_managed and not force:
                        preservadas += 1
                        continue

                    question.statement = qd["statement"]
                    question.explanation = qd.get("explanation", "")
                    question.is_active = True
                    question.seed_managed = True
                    question.save(
                        update_fields=["statement", "explanation", "is_active", "seed_managed"]
                    )
                    self._write_choices(question, qd.get("choices", []))

        if preservadas:
            self.stdout.write(
                self.style.WARNING(
                    f"\n{preservadas} aula(s)/questão(ões) editadas pelo admin foram "
                    "preservadas (use --force para sincronizar mesmo assim)."
                )
            )
        self.stdout.write(self.style.SUCCESS("\nSeed concluído."))

    def _write_choices(self, question: Question, choices_data: list) -> None:
        question.choices.all().delete()
        for ci, choice in enumerate(choices_data):
            Choice.objects.create(
                question=question,
                text=choice["text"][:255],
                is_correct=bool(choice.get("correct", False)),
                order=ci,
            )
