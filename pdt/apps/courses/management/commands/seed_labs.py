"""Carrega os laboratórios práticos no banco. Idempotente e não-destrutivo.

Mesmo padrão de `seed_topics`/`seed_glossary`: um lab editado pelo admin
(`seed_managed=False`) é preservado; use `--force` para sobrescrever mesmo
assim. Cada tópico recebe exatamente 1 lab (chave de identidade = topic),
resolvendo a queixa "não tem laboratório prático de verdade" sem exigir
sandbox real — o `kind` de cada um decide como o Alpine.js no template
interpreta `spec` (ver docstring de `apps.courses.models.Lab`).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.courses.models import Lab, Topic
from apps.courses.seed_data.labs import LABS


class Command(BaseCommand):
    help = "Cria/atualiza os laboratórios práticos interativos de cada tópico."

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

        for entry in LABS:
            try:
                topic = Topic.objects.get(title=entry["topic_title"])
            except Topic.DoesNotExist:
                sem_topico.append(entry["topic_title"])
                continue

            lab, created = Lab.objects.get_or_create(
                topic=topic,
                defaults={
                    "kind": entry["kind"],
                    "title": entry["title"],
                    "title_en": entry.get("title_en", ""),
                    "spec": entry["spec"],
                    "spec_en": entry.get("spec_en"),
                    "order": entry.get("order", 0),
                    "seed_managed": True,
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
            lab.order = entry.get("order", 0)
            lab.seed_managed = True
            lab.save(
                update_fields=[
                    "kind",
                    "title",
                    "title_en",
                    "spec",
                    "spec_en",
                    "order",
                    "seed_managed",
                ]
            )
            atualizados += 1

        self.stdout.write(self.style.SUCCESS(f"{criados} lab(s) criado(s)."))
        self.stdout.write(self.style.SUCCESS(f"{atualizados} lab(s) atualizado(s)."))
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
