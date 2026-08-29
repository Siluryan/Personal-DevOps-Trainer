"""Carrega os laboratórios práticos no banco. Idempotente e não-destrutivo.

Mesmo padrão de `seed_topics`/`seed_glossary`: um lab editado pelo admin
(`seed_managed=False`) é preservado; use `--force` para sobrescrever mesmo
assim. Cada *página* de aula recebe 1 lab (chave = topic + lesson_page).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.courses.models import Lab, Topic
from apps.courses.seed_data.labs import LABS
from apps.courses.seed_data.page_labs import expand_labs


class Command(BaseCommand):
    help = "Cria/atualiza os laboratórios práticos interativos de cada página de aula."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve também labs editados pelo admin (seed_managed=False).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        force = opts["force"]
        preservados = 0
        criados = 0
        atualizados = 0
        sem_topico = []
        wanted_pages: dict[int, set[int]] = {}

        entries = expand_labs()
        authored_page_by_title = {
            e["topic_title"]: e["lesson_page"]
            for e in entries
            if any(lab["title"] == e["title"] and lab["topic_title"] == e["topic_title"] for lab in LABS)
        }
        # Lab único da era "1 por tópico": leva para a página do lab autoral
        # para a conclusão do aluno continuar no mesmo registro.
        for title, page in authored_page_by_title.items():
            try:
                topic = Topic.objects.get(title=title)
            except Topic.DoesNotExist:
                continue
            existing = list(topic.labs.order_by("id"))
            if len(existing) == 1 and existing[0].lesson_page != page:
                if not topic.labs.filter(lesson_page=page).exclude(pk=existing[0].pk).exists():
                    existing[0].lesson_page = page
                    existing[0].save(update_fields=["lesson_page"])

        for entry in entries:
            try:
                topic = Topic.objects.get(title=entry["topic_title"])
            except Topic.DoesNotExist:
                sem_topico.append(entry["topic_title"])
                continue

            page = entry["lesson_page"]
            wanted_pages.setdefault(topic.id, set()).add(page)

            lab, created = Lab.objects.get_or_create(
                topic=topic,
                lesson_page=page,
                defaults={
                    "kind": entry["kind"],
                    "title": entry["title"],
                    "title_en": entry.get("title_en", ""),
                    "spec": entry["spec"],
                    "spec_en": entry.get("spec_en"),
                    "order": entry.get("order", page),
                    "seed_managed": True,
                    "is_active": True,
                },
            )
            if created:
                criados += 1
                continue

            if not lab.seed_managed and not force:
                preservados += 1
                continue

            lab.kind = entry["kind"]
            lab.title = entry["title"]
            lab.title_en = entry.get("title_en", "")
            lab.spec = entry["spec"]
            lab.spec_en = entry.get("spec_en")
            lab.order = entry.get("order", page)
            lab.seed_managed = True
            lab.is_active = True
            lab.save(
                update_fields=[
                    "kind",
                    "title",
                    "title_en",
                    "spec",
                    "spec_en",
                    "order",
                    "seed_managed",
                    "is_active",
                ]
            )
            atualizados += 1

        desativados = 0
        for topic_id, pages in wanted_pages.items():
            extra = Lab.objects.filter(topic_id=topic_id, seed_managed=True).exclude(
                lesson_page__in=pages
            )
            desativados += extra.update(is_active=False)

        self.stdout.write(self.style.SUCCESS(f"{criados} lab(s) criado(s)."))
        self.stdout.write(self.style.SUCCESS(f"{atualizados} lab(s) atualizado(s)."))
        if desativados:
            self.stdout.write(self.style.WARNING(f"{desativados} lab(s) fora da paginação atual desativado(s)."))
        if preservados:
            self.stdout.write(
                self.style.WARNING(
                    f"{preservados} lab(s) editado(s) pelo admin foram preservados "
                    "(use --force para sincronizar mesmo assim)."
                )
            )
        if sem_topico:
            raise CommandError(
                "Tópico(s) não encontrado(s), rode seed_topics antes: "
                + ", ".join(sem_topico)
            )
        self.stdout.write(self.style.SUCCESS("Seed de laboratórios concluído."))
