"""Popula o banco de questões do teste de admissão.

Cada execução do teste sorteia 5 de Linux + 5 de Redes; por isso cadastramos
um banco maior do que 10, o seed também é idempotente.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import AdmissionChoice, AdmissionQuestion
from apps.core.seed_utils import shuffle_seeded


def _q(
    area: str,
    statement: str,
    correct: str,
    wrong: list[str],
    explanation: str = "",
    statement_en: str = "",
    explanation_en: str = "",
    correct_en: str = "",
    wrong_en: list[str] | None = None,
):
    wrong_en = wrong_en or []
    choices = [{"text": correct, "text_en": correct_en, "correct": True}] + [
        {"text": w, "text_en": (wrong_en[i] if i < len(wrong_en) else ""), "correct": False}
        for i, w in enumerate(wrong)
    ]
    # Determinístico por enunciado: a ordem não muda a cada restart do processo.
    shuffle_seeded(choices, statement)
    return {
        "area": area,
        "statement": statement,
        "statement_en": statement_en,
        "explanation": explanation,
        "explanation_en": explanation_en,
        "choices": choices,
    }


LINUX = AdmissionQuestion.LINUX
NETWORK = AdmissionQuestion.NETWORK


QUESTIONS = [
    # Linux
    _q(LINUX, "Em Linux, o que faz `chmod 644 arquivo`?",
       "Dá leitura/escrita para o dono e leitura para grupo e outros.",
       ["Dá leitura e execução para o dono, sem acesso para o resto.", "Dá permissão total para o dono e execução para o grupo.", "Bloqueia leitura e escrita para o dono, liberando o resto."],
       "6 = rw, 4 = r.",
       statement_en="In Linux, what does `chmod 644 file` do?",
       correct_en="Gives the owner read/write and gives group and others read-only.",
       wrong_en=["Gives the owner read and execute, with no access for everyone else.", "Gives the owner full permission and gives the group execute.", "Blocks read and write for the owner while opening up the rest."],
       explanation_en="6 = rw, 4 = r."),
    _q(LINUX, "Qual comando lista processos em execução?",
       "ps", ["chmod", "ls", "tar"], "",
       statement_en="Which command lists running processes?",
       correct_en="ps", wrong_en=["chmod", "ls", "tar"], explanation_en=""),
    _q(LINUX, "O que representa `/etc/passwd`?",
       "Arquivo com usuários do sistema (UIDs, shells).",
       ["Guarda os hashes de senha de cada usuário.", "Mapeia as partições de disco montadas no sistema.", "Define as regras de firewall do sistema."], "",
       statement_en="What does `/etc/passwd` represent?",
       correct_en="File with the system's users (UIDs, shells).",
       wrong_en=["Stores the password hash for each user.", "Maps the disk partitions mounted on the system.", "Defines the system's firewall rules."],
       explanation_en=""),
    _q(LINUX, "Como exibir o conteúdo de um arquivo de texto pequeno?",
       "cat arquivo.txt", ["touch arquivo.txt", "echo arquivo.txt", "find arquivo.txt"], "",
       statement_en="How do you display the contents of a small text file?",
       correct_en="cat file.txt", wrong_en=["touch file.txt", "echo file.txt", "find file.txt"], explanation_en=""),
    _q(LINUX, "Qual diretório guarda configurações do sistema?",
       "/etc", ["/var", "/usr/bin", "/home"], "",
       statement_en="Which directory holds system configuration?",
       correct_en="/etc", wrong_en=["/var", "/usr/bin", "/home"], explanation_en=""),
    _q(LINUX, "O que é UID 0?",
       "ID do superusuário (root).",
       ["ID reservado para processos de rede.", "ID do primeiro usuário criado manualmente.", "ID que qualquer processo pode assumir sem privilégio."], "",
       statement_en="What is UID 0?",
       correct_en="The superuser's ID (root).",
       wrong_en=["An ID reserved for network processes.", "The ID of the first manually created user.", "An ID any process can take on without any privilege."],
       explanation_en=""),
    _q(LINUX, "Como ver o uso de espaço de disco geral?",
       "df -h", ["du -sh /etc", "ls -la /", "free -m"], "df mostra filesystems montados.",
       statement_en="How do you check overall disk space usage?",
       correct_en="df -h", wrong_en=["du -sh /etc", "ls -la /", "free -m"],
       explanation_en="df shows mounted filesystems."),
    _q(LINUX, "Qual sinal `kill -9` envia?",
       "SIGKILL, termina o processo imediatamente.",
       ["SIGTERM, pede o encerramento e permite cleanup antes de sair.", "SIGSTOP, pausa a execução sem encerrar o processo.", "SIGHUP, recarrega a configuração sem reiniciar o serviço."], "",
       statement_en="Which signal does `kill -9` send?",
       correct_en="SIGKILL, ends the process immediately.",
       wrong_en=["SIGTERM, asks it to shut down and allows cleanup before exiting.", "SIGSTOP, pauses execution without ending the process.", "SIGHUP, reloads the configuration without restarting the service."],
       explanation_en=""),
    _q(LINUX, "Onde olhar logs do sistema em distros com systemd?",
       "journalctl",
       ["/etc/log", "syslogctl", "ls /var/log/.cache"], "",
       statement_en="Where do you check system logs on distros using systemd?",
       correct_en="journalctl", wrong_en=["/etc/log", "syslogctl", "ls /var/log/.cache"], explanation_en=""),
    _q(LINUX, "Para que serve `sudo`?",
       "Executar comandos com privilégios elevados conforme regras.",
       ["Trocar de usuário automaticamente a cada login, sem senha.", "Compactar e enviar arquivos de log para outro servidor.", "Renomear binários do sistema durante uma atualização."], "",
       statement_en="What is `sudo` for?",
       correct_en="Running commands with elevated privileges according to defined rules.",
       wrong_en=["Automatically switching between user accounts on every login, without requiring a password.", "Compressing and sending log files to another server.", "Renaming system binaries during an update."],
       explanation_en=""),
    _q(LINUX, "`cd ~` leva para:",
       "Diretório home do usuário atual.",
       ["Diretório temporário limpo a cada reinício do sistema.", "Diretório de configuração global do usuário root.", "Diretório onde ficam os binários do sistema operacional."], "",
       statement_en="`cd ~` takes you to:",
       correct_en="The current user's home directory.",
       wrong_en=["A temporary directory cleared on every system reboot.", "The root user's global configuration directory.", "The directory holding the operating system's binaries."],
       explanation_en=""),
    _q(LINUX, "Qual variável guarda o caminho dos executáveis do shell?",
       "PATH",
       ["HOME", "USER", "TERM"], "",
       statement_en="Which variable holds the shell's executable search path?",
       correct_en="PATH", wrong_en=["HOME", "USER", "TERM"], explanation_en=""),

    # Redes
    _q(NETWORK, "Qual a porta padrão do HTTPS?",
       "443", ["80", "22", "8080"], "",
       statement_en="What is the default HTTPS port?",
       correct_en="443", wrong_en=["80", "22", "8080"], explanation_en=""),
    _q(NETWORK, "TCP é um protocolo:",
       "Orientado a conexão (com handshake).",
       ["Sem conexão, cada pacote segue caminho independente.", "Multicast por padrão, um remetente para vários destinos.", "Exclusivo para tráfego IPv6, sem suporte a IPv4."], "",
       statement_en="TCP is a protocol that is:",
       correct_en="Connection-oriented (with a handshake).",
       wrong_en=["Connectionless, with each packet following an independent path.", "Multicast by default, one sender to several destinations.", "Exclusive to IPv6 traffic, with no support for IPv4."],
       explanation_en=""),
    _q(NETWORK, "DNS serve para:",
       "Resolver nomes de domínio em endereços IP.",
       ["Definir as rotas entre redes diferentes na internet.", "Comprimir pacotes para reduzir uso de banda.", "Cifrar dados armazenados em disco no servidor."], "",
       statement_en="DNS is used to:",
       correct_en="Resolve domain names into IP addresses.",
       wrong_en=["Define the routes between different networks on the internet.", "Compress packets to reduce bandwidth usage.", "Encrypt data stored on the server's disk."],
       explanation_en=""),
    _q(NETWORK, "127.0.0.1 é:",
       "Endereço de loopback IPv4.",
       ["Endereço reservado para a rede local (LAN).", "Endereço do roteador padrão da rede.", "Endereço do servidor DNS público mais usado."], "",
       statement_en="127.0.0.1 is:",
       correct_en="The IPv4 loopback address.",
       wrong_en=["An address reserved for the local network (LAN).", "The network's default router address.", "The most commonly used public DNS server address."],
       explanation_en=""),
    _q(NETWORK, "Qual ferramenta lista sockets em escuta no Linux?",
       "ss -tulpn", ["ifconfig", "netstat -tulpn", "ipset -L"], "",
       statement_en="Which tool lists listening sockets on Linux?",
       correct_en="ss -tulpn", wrong_en=["ifconfig", "netstat -tulpn", "ipset -L"], explanation_en=""),
    _q(NETWORK, "CIDR /24 corresponde a quantos hosts utilizáveis aproximadamente?",
       "254", ["1024", "65 mil", "2"], "256 - 2 (rede e broadcast).",
       statement_en="A /24 CIDR corresponds to roughly how many usable hosts?",
       correct_en="254", wrong_en=["1024", "65 thousand", "2"],
       explanation_en="256 - 2 (network and broadcast)."),
    _q(NETWORK, "Qual porta padrão do SSH?",
       "22", ["80", "443", "21"], "",
       statement_en="What is the default SSH port?",
       correct_en="22", wrong_en=["80", "443", "21"], explanation_en=""),
    _q(NETWORK, "ICMP é usado por:",
       "ping e traceroute.",
       ["Requisições HTTP para páginas web.", "Consultas DNS para resolver nomes.", "Conexões SSH para acesso remoto."], "",
       statement_en="ICMP is used by:",
       correct_en="ping and traceroute.",
       wrong_en=["HTTP requests for web pages.", "DNS queries to resolve names.", "SSH connections for remote access."],
       explanation_en=""),
    _q(NETWORK, "UDP é mais comum em:",
       "DNS, voz/vídeo em tempo real.",
       ["Transferência confiável de arquivos.", "Conexões remotas via SSH.", "Envio de mensagens de e-mail."], "",
       statement_en="UDP is most common in:",
       correct_en="DNS, real-time voice/video.",
       wrong_en=["Reliable file transfer.", "Remote connections over SSH.", "Sending email messages."],
       explanation_en=""),
    _q(NETWORK, "O comando `traceroute` mostra:",
       "Caminho dos pacotes até o destino.",
       ["A latência total da conexão, sem detalhes de rota.", "O nome do domínio resolvido pelo DNS.", "A velocidade de download disponível no link."], "",
       statement_en="The `traceroute` command shows:",
       correct_en="The path packets take to the destination.",
       wrong_en=["The connection's total latency, without route detail.", "The domain name resolved by DNS.", "The download speed available on the link."],
       explanation_en=""),
    _q(NETWORK, "O que faz um proxy reverso?",
       "Recebe requisições do cliente e encaminha ao backend.",
       ["Faz cache de respostas de DNS para acelerar consultas.", "Substitui completamente a necessidade de firewall na rede.", "Comprime arquivos estáticos antes de enviar ao cliente."], "",
       statement_en="What does a reverse proxy do?",
       correct_en="Receives client requests and forwards them to the backend.",
       wrong_en=["Caches DNS responses to speed up lookups.", "Completely removes the need for a firewall on the network.", "Compresses static files before sending them to the client."],
       explanation_en=""),
    _q(NETWORK, "TLS protege:",
       "Comunicação em trânsito.",
       ["Dados armazenados em disco, já gravados.", "Consultas DNS recursivas na rede interna.", "Senhas guardadas no gerenciador do sistema."], "",
       statement_en="TLS protects:",
       correct_en="Communication in transit.",
       wrong_en=["Data already stored on disk.", "Recursive DNS queries on the internal network.", "Passwords stored in the system's manager."],
       explanation_en=""),
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
                    "statement_en": entry.get("statement_en", ""),
                    "explanation": entry.get("explanation", ""),
                    "explanation_en": entry.get("explanation_en", ""),
                    "is_active": True,
                },
            )
            if not was_created:
                question.area = entry["area"]
                question.statement_en = entry.get("statement_en", "")
                question.explanation = entry.get("explanation", "")
                question.explanation_en = entry.get("explanation_en", "")
                question.is_active = True
                question.save()
            question.choices.all().delete()
            for i, c in enumerate(entry["choices"]):
                AdmissionChoice.objects.create(
                    question=question,
                    text=c["text"][:255],
                    text_en=c.get("text_en", "")[:255],
                    is_correct=c.get("correct", False),
                    order=i,
                )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Banco com {AdmissionQuestion.objects.count()} questões "
                                             f"({created} novas)."))
