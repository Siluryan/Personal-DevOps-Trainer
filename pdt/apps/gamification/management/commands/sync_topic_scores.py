"""Realinha `TopicScore` com as tentativas de quiz já gravadas.

Antes isto rodava dentro de `top_users()`, ou seja, a cada GET do ranking —
que é uma página pública e anônima. Qualquer visitante disparava um loop de
UPDATEs no banco. O caminho normal de atualização é
`TopicScore.update_from_attempt`, chamado ao enviar o quiz; este comando é a
rede de segurança para corrigir desvios históricos.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.gamification.services import sync_topic_scores_for_public_users


class Command(BaseCommand):
    help = "Realinha TopicScore com o melhor score de cada tentativa registrada."

    def handle(self, *args, **options):
        corrigidos = sync_topic_scores_for_public_users()
        if corrigidos:
            self.stdout.write(
                self.style.SUCCESS(f"{corrigidos} registro(s) de TopicScore corrigido(s).")
            )
        else:
            self.stdout.write("Nada a corrigir: os scores já estão alinhados.")
