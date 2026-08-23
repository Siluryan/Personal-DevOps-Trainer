"""Carrega os termos de glossário no banco. Idempotente e não-destrutivo.

Segue o mesmo padrão de `courses.seed_topics`: um termo editado pelo admin
(`seed_managed=False`) é preservado; use `--force` para sobrescrever mesmo
assim.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import GlossaryTerm
from apps.core.seed_data.glossary import GLOSSARY_TERMS


class Command(BaseCommand):
    help = "Cria/atualiza os termos de glossário usados nas caixinhas clicáveis das aulas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescreve também termos editados pelo admin (seed_managed=False).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        force = opts["force"]
        preservados = 0
        criados = 0
        atualizados = 0

        for entry in GLOSSARY_TERMS:
            term, created = GlossaryTerm.objects.get_or_create(
                term=entry["term"],
                defaults={"definition": entry["definition"], "seed_managed": True},
            )
            if created:
                criados += 1
                continue

            if not term.seed_managed and not force:
                preservados += 1
                continue

            term.definition = entry["definition"]
            term.seed_managed = True
            term.save(update_fields=["definition", "seed_managed"])
            atualizados += 1

        self.stdout.write(self.style.SUCCESS(f"{criados} termo(s) criado(s)."))
        self.stdout.write(self.style.SUCCESS(f"{atualizados} termo(s) atualizado(s)."))
        if preservados:
            self.stdout.write(
                self.style.WARNING(
                    f"{preservados} termo(s) editado(s) pelo admin foram preservados "
                    "(use --force para sincronizar mesmo assim)."
                )
            )
        self.stdout.write(self.style.SUCCESS("Seed de glossário concluído."))
