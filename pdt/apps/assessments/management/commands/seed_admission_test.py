"""Popula o banco de questões do teste de admissão.

Cada execução do teste sorteia 5 de Linux + 5 de Redes; por isso cadastramos
um banco maior do que 10, o seed também é idempotente.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AdmissionChoice, AdmissionQuestion
from apps.core.seed_utils import shuffle_seeded


def _q(area: str, statement: str, correct: str, wrong: list[str], explanation: str = ""):
    choices = [{"text": correct, "correct": True}] + [
        {"text": w, "correct": False} for w in wrong
    ]
    # Determinístico por enunciado: a ordem não muda a cada restart do processo.
    shuffle_seeded(choices, statement)
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
       ["Dá leitura e execução para o dono, sem acesso para o resto.", "Dá permissão total para o dono e execução para o grupo.", "Bloqueia leitura e escrita para o dono, liberando o resto."],
       "6 = rw, 4 = r."),
    _q(LINUX, "Qual comando lista processos em execução?",
       "ps", ["chmod", "ls", "tar"], ""),
    _q(LINUX, "O que representa `/etc/passwd`?",
       "Arquivo com usuários do sistema (UIDs, shells).",
       ["Guarda os hashes de senha de cada usuário.", "Mapeia as partições de disco montadas no sistema.", "Define as regras de firewall do sistema."], ""),
    _q(LINUX, "Como exibir o conteúdo de um arquivo de texto pequeno?",
       "cat arquivo.txt", ["touch arquivo.txt", "echo arquivo.txt", "find arquivo.txt"], ""),
    _q(LINUX, "Qual diretório guarda configurações do sistema?",
       "/etc", ["/var", "/usr/bin", "/home"], ""),
    _q(LINUX, "O que é UID 0?",
       "ID do superusuário (root).",
       ["ID reservado para processos de rede.", "ID do primeiro usuário criado manualmente.", "ID que qualquer processo pode assumir sem privilégio."], ""),
    _q(LINUX, "Como ver o uso de espaço de disco geral?",
       "df -h", ["du -sh /etc", "ls -la /", "free -m"], "df mostra filesystems montados."),
    _q(LINUX, "Qual sinal `kill -9` envia?",
       "SIGKILL, termina o processo imediatamente.",
       ["SIGTERM, pede o encerramento e permite cleanup antes de sair.", "SIGSTOP, pausa a execução sem encerrar o processo.", "SIGHUP, recarrega a configuração sem reiniciar o serviço."], ""),
    _q(LINUX, "Onde olhar logs do sistema em distros com systemd?",
       "journalctl",
       ["/etc/log", "syslogctl", "ls /var/log/.cache"], ""),
    _q(LINUX, "Para que serve `sudo`?",
       "Executar comandos com privilégios elevados conforme regras.",
       ["Trocar de usuário automaticamente a cada login, sem senha.", "Compactar e enviar arquivos de log para outro servidor.", "Renomear binários do sistema durante uma atualização."], ""),
    _q(LINUX, "`cd ~` leva para:",
       "Diretório home do usuário atual.",
       ["Diretório temporário limpo a cada reinício do sistema.", "Diretório de configuração global do usuário root.", "Diretório onde ficam os binários do sistema operacional."], ""),
    _q(LINUX, "Qual variável guarda o caminho dos executáveis do shell?",
       "PATH",
       ["HOME", "USER", "TERM"], ""),

    # Redes
    _q(NETWORK, "Qual a porta padrão do HTTPS?",
       "443", ["80", "22", "8080"], ""),
    _q(NETWORK, "TCP é um protocolo:",
       "Orientado a conexão (com handshake).",
       ["Sem conexão, cada pacote segue caminho independente.", "Multicast por padrão, um remetente para vários destinos.", "Exclusivo para tráfego IPv6, sem suporte a IPv4."], ""),
    _q(NETWORK, "DNS serve para:",
       "Resolver nomes de domínio em endereços IP.",
       ["Definir as rotas entre redes diferentes na internet.", "Comprimir pacotes para reduzir uso de banda.", "Cifrar dados armazenados em disco no servidor."], ""),
    _q(NETWORK, "127.0.0.1 é:",
       "Endereço de loopback IPv4.",
       ["Endereço reservado para a rede local (LAN).", "Endereço do roteador padrão da rede.", "Endereço do servidor DNS público mais usado."], ""),
    _q(NETWORK, "Qual ferramenta lista sockets em escuta no Linux?",
       "ss -tulpn", ["ifconfig", "netstat -tulpn", "ipset -L"], ""),
    _q(NETWORK, "CIDR /24 corresponde a quantos hosts utilizáveis aproximadamente?",
       "254", ["1024", "65 mil", "2"], "256 - 2 (rede e broadcast)."),
    _q(NETWORK, "Qual porta padrão do SSH?",
       "22", ["80", "443", "21"], ""),
    _q(NETWORK, "ICMP é usado por:",
       "ping e traceroute.",
       ["Requisições HTTP para páginas web.", "Consultas DNS para resolver nomes.", "Conexões SSH para acesso remoto."], ""),
    _q(NETWORK, "UDP é mais comum em:",
       "DNS, voz/vídeo em tempo real.",
       ["Transferência confiável de arquivos.", "Conexões remotas via SSH.", "Envio de mensagens de e-mail."], ""),
    _q(NETWORK, "O comando `traceroute` mostra:",
       "Caminho dos pacotes até o destino.",
       ["A latência total da conexão, sem detalhes de rota.", "O nome do domínio resolvido pelo DNS.", "A velocidade de download disponível no link."], ""),
    _q(NETWORK, "O que faz um proxy reverso?",
       "Recebe requisições do cliente e encaminha ao backend.",
       ["Faz cache de respostas de DNS para acelerar consultas.", "Substitui completamente a necessidade de firewall na rede.", "Comprime arquivos estáticos antes de enviar ao cliente."], ""),
    _q(NETWORK, "TLS protege:",
       "Comunicação em trânsito.",
       ["Dados armazenados em disco, já gravados.", "Consultas DNS recursivas na rede interna.", "Senhas guardadas no gerenciador do sistema."], ""),
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
