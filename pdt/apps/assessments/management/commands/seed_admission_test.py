"""Popula o banco de questões do teste de admissão.

Cada execução do teste sorteia 5 de Linux + 5 de Redes; por isso cadastramos
um banco maior do que 10, o seed também é idempotente.
"""
from __future__ import annotations

import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AdmissionChoice, AdmissionQuestion


def _q(area: str, statement: str, correct: str, wrong: list[str], explanation: str = ""):
    choices = [{"text": correct, "correct": True}] + [
        {"text": w, "correct": False} for w in wrong
    ]
    random.shuffle(choices)
    return {
        "area": area,
        "statement": statement,
        "explanation": explanation,
        "choices": choices,
    }


LINUX = AdmissionQuestion.LINUX
NETWORK = AdmissionQuestion.NETWORK


QUESTIONS = [
    # Linux
    _q(LINUX, "Em Linux, o que faz `chmod 644 arquivo`?",
       "Dá leitura/escrita para o dono e leitura para grupo e outros.",
       ["Permissão total para todos.", "Apenas execução para o dono.", "Bloqueia acesso a todos."],
       "6 = rw, 4 = r."),
    _q(LINUX, "Qual comando lista processos em execução?",
       "ps", ["chmod", "ls", "tar"], ""),
    _q(LINUX, "O que representa `/etc/passwd`?",
       "Arquivo com usuários do sistema (UIDs, shells).",
       ["Hashes de senha.", "Tabela de partições.", "Configuração do nginx."], ""),
    _q(LINUX, "Como exibir o conteúdo de um arquivo de texto pequeno?",
       "cat arquivo.txt", ["touch arquivo.txt", "echo arquivo.txt", "find arquivo.txt"], ""),
    _q(LINUX, "Qual diretório guarda configurações do sistema?",
       "/etc", ["/var", "/usr/bin", "/home"], ""),
    _q(LINUX, "O que é UID 0?",
       "ID do superusuário (root).",
       ["Usuário convidado.", "Bloqueado.", "Apenas teste."], ""),
    _q(LINUX, "Como ver o uso de espaço de disco geral?",
       "df -h", ["du -sh /etc", "ls -la /", "free -m"], "df mostra filesystems montados."),
    _q(LINUX, "Qual sinal `kill -9` envia?",
       "SIGKILL, termina o processo imediatamente.",
       ["SIGTERM com cleanup.", "SIGSTOP pausa.", "SIGHUP recarrega config."], ""),
    _q(LINUX, "Onde olhar logs do sistema em distros com systemd?",
       "journalctl",
       ["/etc/log", "syslogctl", "ls /var/log/.cache"], ""),
    _q(LINUX, "Para que serve `sudo`?",
       "Executar comandos com privilégios elevados conforme regras.",
       ["Trocar usuário no chat.", "Compactar arquivos.", "Renomear binários."], ""),
    _q(LINUX, "`cd ~` leva para:",
       "Diretório home do usuário atual.",
       ["Raiz do sistema.", "/etc.", "/var."], ""),
    _q(LINUX, "Qual variável guarda o caminho dos executáveis do shell?",
       "PATH",
       ["HOME", "USER", "TERM"], ""),

    # Redes
    _q(NETWORK, "Qual a porta padrão do HTTPS?",
       "443", ["80", "22", "8080"], ""),
    _q(NETWORK, "TCP é um protocolo:",
       "Orientado a conexão (com handshake).",
       ["Sem conexão.", "Multicast por padrão.", "Apenas IPv6."], ""),
    _q(NETWORK, "DNS serve para:",
       "Resolver nomes de domínio em endereços IP.",
       ["Roteamento.", "Compressão.", "Criptografia em repouso."], ""),
    _q(NETWORK, "127.0.0.1 é:",
       "Endereço de loopback IPv4.",
       ["IP público.", "Roteador padrão.", "DNS do Google."], ""),
    _q(NETWORK, "Qual ferramenta lista sockets em escuta no Linux?",
       "ss -tulpn", ["ifconfig", "route", "ipset"], ""),
    _q(NETWORK, "CIDR /24 corresponde a quantos hosts utilizáveis aproximadamente?",
       "254", ["1024", "65 mil", "Apenas 1"], "256 - 2 (rede e broadcast)."),
    _q(NETWORK, "Qual porta padrão do SSH?",
       "22", ["80", "443", "21"], ""),
    _q(NETWORK, "ICMP é usado por:",
       "ping e traceroute.", ["HTTP requests.", "DNS queries.", "Apenas SSH."], ""),
    _q(NETWORK, "UDP é mais comum em:",
       "DNS, voz/vídeo em tempo real.",
       ["Transferência confiável de arquivos.", "Apenas SSH.", "Apenas e-mail."], ""),
    _q(NETWORK, "O comando `traceroute` mostra:",
       "Caminho dos pacotes até o destino.",
       ["Apenas o IP.", "Apenas a porta.", "Apenas TLS."], ""),
    _q(NETWORK, "O que faz um proxy reverso?",
       "Recebe requisições do cliente e encaminha ao backend.",
       ["Apenas faz cache de DNS.", "Substitui firewall.", "Apenas comprime arquivos."], ""),
    _q(NETWORK, "TLS protege:",
       "Comunicação em trânsito.",
       ["Apenas dados em repouso.", "Apenas DNS recursivo.", "Apenas senha do sistema."], ""),
]


class Command(BaseCommand):
    help = "Popula o banco de questões do teste de admissão (Linux + Redes)."

    @transaction.atomic
    def handle(self, *args, **opts):
        created = 0
        for entry in QUESTIONS:
            question, was_created = AdmissionQuestion.objects.get_or_create(
                statement=entry["statement"],
                defaults={
                    "area": entry["area"],
                    "explanation": entry.get("explanation", ""),
                    "is_active": True,
                },
            )
            if not was_created:
                question.area = entry["area"]
                question.explanation = entry.get("explanation", "")
                question.is_active = True
                question.save()
            question.choices.all().delete()
            for i, c in enumerate(entry["choices"]):
                AdmissionChoice.objects.create(
                    question=question,
                    text=c["text"][:255],
                    is_correct=c.get("correct", False),
                    order=i,
                )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Banco com {AdmissionQuestion.objects.count()} questões "
                                             f"({created} novas)."))
