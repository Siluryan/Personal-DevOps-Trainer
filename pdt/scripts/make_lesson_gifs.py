"""Gera GIFs de arquitetura das aulas e aponta os HTML do seed para eles.

Roda uma vez: python3 pdt/scripts/make_lesson_gifs.py
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "static" / "img" / "lessons"
SEED = ROOT / "apps" / "courses" / "seed_data"
W, H = 960, 540
FRAMES = 10
BG = (7, 9, 15)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
FONT_SM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
FONT_LG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
FONT_MD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

ACCENTS = ["#38bdf8", "#34d399", "#fbbf24", "#c084fc", "#fb7185", "#94a3b8"]


def hex_color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, xy, text, font, fill):
    w, h = text_size(draw, text, font)
    draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=font, fill=fill)


def dashed_rect(draw, box, color, phase, width=2):
    x1, y1, x2, y2 = box
    span = [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]
    dash, gap = 10, 7
    shift = (phase * 3) % (dash + gap)
    for ax, ay, bx, by in span:
        length = math.hypot(bx - ax, by - ay)
        if length == 0:
            continue
        ux, uy = (bx - ax) / length, (by - ay) / length
        pos = -shift
        while pos < length:
            start = max(0, pos)
            end = min(length, pos + dash)
            if end > start:
                draw.line(
                    [(ax + ux * start, ay + uy * start), (ax + ux * end, ay + uy * end)],
                    fill=color,
                    width=width,
                )
            pos += dash + gap


def arrow(draw, p1, p2, color, phase, width=3, head=True):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    # para a ponta não entrar no nó
    end = (x2 - ux * 12, y2 - uy * 12)
    dash, gap = 14, 8
    shift = (phase * 4) % (dash + gap)
    pos = 0
    while pos < length - 12:
        a = pos + shift
        b = min(length - 12, a + dash)
        if b > 0 and a < length - 12:
            a = max(0, a)
            draw.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)], fill=color, width=width)
        pos += dash + gap
    ang = math.atan2(uy, ux)
    if head:
        head_len = 11
        pts = [
            end,
            (end[0] - head_len * math.cos(ang - 0.45), end[1] - head_len * math.sin(ang - 0.45)),
            (end[0] - head_len * math.cos(ang + 0.45), end[1] - head_len * math.sin(ang + 0.45)),
        ]
        draw.polygon(pts, fill=color)
    t = ((phase + 3) % FRAMES) / FRAMES
    dot = (x1 + (end[0] - x1) * t, y1 + (end[1] - y1) * t)
    r = 5
    draw.ellipse((dot[0] - r, dot[1] - r, dot[0] + r, dot[1] + r), fill=(240, 249, 255))


def round_node(draw, cx, cy, label, accent, phase, w=168):
    h = 52
    x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    draw.rounded_rectangle((x1, y1, x2, y2), radius=12, fill=(16, 22, 34), outline=accent, width=2)
    draw.rounded_rectangle((x1, y1, x1 + 8, y2), radius=3, fill=accent)
    # brilho leve no quadro do frame, para o GIF não parecer estático mesmo num nó
    if phase % 5 == int(cx) % 5:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=12, outline=(255, 255, 255), width=1)
    center_text(draw, (cx + 4, cy), label, FONT_MD, (232, 240, 248))


def hex_node(draw, cx, cy, label, fill):
    r = 26
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=(232, 240, 248))
    center_text(draw, (cx, cy + r + 16), label, FONT_SM, (226, 232, 240))


def blank(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((28, 16), title, font=FONT_LG, fill=(125, 211, 252))
    return img, draw


def draw_columns(title, columns, phase):
    img, draw = blank(title)
    n = max(1, len(columns))
    gap = 18
    left = 24
    usable = W - 48
    col_w = usable / n
    top, bottom = 64, H - 28
    centers = []
    for i, (group, nodes) in enumerate(columns):
        accent = hex_color(ACCENTS[i % len(ACCENTS)])
        x1 = left + i * col_w + 6
        x2 = left + (i + 1) * col_w - 6
        dashed_rect(draw, (x1, top, x2, bottom), accent, phase)
        center_text(draw, ((x1 + x2) / 2, top + 22), group, FONT_MD, accent)
        count = max(1, len(nodes))
        inner_top = top + 52
        inner_h = bottom - inner_top - 16
        step = inner_h / count
        node_w = min(168, max(96, (x2 - x1) - 28))
        col_centers = []
        for j, label in enumerate(nodes):
            cy = inner_top + step * j + step / 2
            cx = (x1 + x2) / 2
            round_node(draw, cx, cy, label, accent, phase, w=node_w)
            col_centers.append((cx, cy, node_w))
        centers.append(col_centers)
    for i in range(len(centers) - 1):
        src = centers[i]
        dst = centers[i + 1]
        pairs = list(zip(src, dst)) or []
        if len(src) == 1:
            pairs = [(src[0], d) for d in dst]
        elif len(dst) == 1:
            pairs = [(s, dst[0]) for s in src]
        accent = hex_color(ACCENTS[(i + 1) % len(ACCENTS)])
        for a, b in pairs:
            arrow(draw, (a[0] + a[2] / 2 + 2, a[1]), (b[0] - b[2] / 2 - 2, b[1]), accent, phase)
    return img


def draw_cycle(title, labels, phase):
    img, draw = blank(title)
    pts = [(480, 120), (760, 270), (480, 430), (200, 270)]
    accent = hex_color("#38bdf8")
    for i, (label, (cx, cy)) in enumerate(zip(labels, pts)):
        round_node(draw, cx, cy, label, accent, phase)
    order = [0, 1, 2, 3, 0]
    for i in range(4):
        a, b = pts[order[i]], pts[order[i + 1]]
        # empurra a seta para fora da caixa
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1
        ux, uy = vx / length, vy / length
        arrow(draw, (a[0] + ux * 90, a[1] + uy * 36), (b[0] - ux * 90, b[1] - uy * 36), accent, (phase + i * 2) % FRAMES)
    return img


def draw_fanout(title, hub, leaves, phase):
    img, draw = blank(title)
    accent = hex_color("#38bdf8")
    leaf_c = hex_color("#34d399")
    hx, hy = 230, H / 2 + 10
    round_node(draw, hx, hy, hub, accent, phase)
    count = max(1, len(leaves))
    top, bottom = 90, H - 40
    step = (bottom - top) / count
    for i, label in enumerate(leaves):
        cy = top + step * i + step / 2
        cx = 700
        round_node(draw, cx, cy, label, leaf_c, phase)
        arrow(draw, (hx + 86, hy), (cx - 86, cy), leaf_c, (phase + i) % FRAMES)
    return img


def draw_k8s(title, lang, phase):
    img, draw = blank(title)
    client = "Cliente" if lang == "pt" else "Client"
    green = hex_color("#34d399")
    gold = hex_color("#fbbf24")
    blue = hex_color("#60a5fa")
    dashed_rect(draw, (16, 78, 400, 520), green, phase)
    dashed_rect(draw, (500, 78, 944, 520), gold, phase)
    center_text(draw, (208, 98), "Control plane", FONT_MD, green)
    center_text(draw, (722, 98), "Workers", FONT_MD, gold)
    nodes = {
        "cm": (110, 190, "Controller"),
        "ccm": (300, 190, "Cloud"),
        "api": (205, 310, "API"),
        "etcd": (110, 430, "etcd"),
        "sched": (300, 430, "Scheduler"),
    }
    for key, (x, y, label) in nodes.items():
        hex_node(draw, x, y, label, blue if key == "api" else hex_color("#1d4ed8"))
    workers = []
    for col, name in enumerate(("Worker 1", "Worker 2", "Worker 3")):
        cx = 590 + col * 120
        center_text(draw, (cx, 126), name, FONT_SM, gold)
        hex_node(draw, cx, 210, "kubelet", hex_color("#0ea5e9"))
        hex_node(draw, cx, 330, "kube-proxy", hex_color("#0284c7"))
        hex_node(draw, cx, 450, "pod", hex_color("#22c55e"))
        workers.append((cx, 210))
    round_node(draw, 780, 36, client, gold, phase, w=150)
    api = nodes["api"][:2]
    sky = hex_color("#7dd3fc")
    # cliente contorna por cima e desce no vão entre as caixas, sem cortar os workers
    route = [
        ((705, 36), (450, 36)),
        ((450, 36), (450, api[1])),
        ((450, api[1]), (api[0] + 36, api[1])),
    ]
    for i, (a, b) in enumerate(route):
        arrow(draw, a, b, sky, (phase + i * 3) % FRAMES, width=2, head=i == len(route) - 1)
    pairs = [
        (api, nodes["etcd"][:2]),
        (api, nodes["sched"][:2]),
        (api, nodes["cm"][:2]),
        (api, nodes["ccm"][:2]),
    ]
    for cx, cy in workers:
        pairs.append(((api[0] + 26, api[1]), (cx - 26, cy)))
        # ao lado do rótulo, para a linha não atravessar o hex nem o texto
        pairs.append(((cx + 34, cy + 26), (cx + 34, 330 - 26)))
        pairs.append(((cx + 34, 330 + 26), (cx + 34, 450 - 26)))
    for i, (a, b) in enumerate(pairs):
        arrow(draw, a, b, sky, (phase + i) % FRAMES, width=2)
    return img


def render(kind, title, payload, lang) -> Image.Image:
    frames = []
    for phase in range(FRAMES):
        if kind == "cols":
            frames.append(draw_columns(title, payload, phase))
        elif kind == "cycle":
            frames.append(draw_cycle(title, payload, phase))
        elif kind == "fanout":
            frames.append(draw_fanout(title, payload[0], payload[1], phase))
        elif kind == "k8s":
            frames.append(draw_k8s(title, lang, phase))
        else:
            raise SystemExit(kind)
    return frames


def save_gif(frames: list[Image.Image], path: Path) -> None:
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=140,
        loop=0,
        optimize=True,
        disposal=2,
    )


def figure(src: str, alt: str, caption: str) -> str:
    return (
        '<figure class="lesson-figure">\n'
        f'<img src="/static/img/lessons/{src}" alt="{alt}">\n'
        f"<figcaption>{caption}</figcaption>\n"
        "</figure>"
    )


def insert_after(chunk: str, h3: str, html: str) -> str:
    needle = f"<h3>{h3}</h3>"
    idx = chunk.find(needle)
    if idx < 0:
        raise SystemExit(f"h3 ausente: {h3}")
    if f"{needle}\n<figure class=\"lesson-figure\">" in chunk[idx : idx + 80] or chunk[idx + len(needle) :].lstrip().startswith("<figure"):
        return chunk
    line_start = chunk.rfind("\n", 0, idx) + 1
    line_end = chunk.find("\n", idx)
    if line_end < 0:
        line_end = len(chunk)
    line = chunk[line_start:line_end]
    indent = re.match(r"\s*", line).group(0)
    if line.rstrip().endswith(('</h3>"', "</h3>'")):
        block = f'\n{indent}"""\n{html}\n"""'
        return chunk[:line_end] + block + chunk[line_end:]
    return chunk[: idx + len(needle)] + "\n" + html + chunk[idx + len(needle) :]


# (tópico, seção, kind, título pt, título en, payload pt, payload en, alt/cap pt, alt/cap en, arquivo)
# payload cols: [(grupo, [nós])...]
# payload cycle: [rótulos]
# payload fanout: (hub, [folhas])
def C(topic, section, kind, title_pt, title_en, pt, en, cap_pt, cap_en, file, cap_en_real=None, file_real=None):
    if kind == "fanout":
        hub_pt, leaves_pt = pt, en
        hub_en, leaves_en = cap_pt, cap_en
        cap_pt, cap_en, file = file, cap_en_real, file_real
        pt = (hub_pt, leaves_pt)
        en = (hub_en, leaves_en)
    return {
        "topic": topic,
        "section": section,
        "kind": kind,
        "title": {"pt": title_pt, "en": title_en},
        "payload": {"pt": pt, "en": en},
        "alt": {"pt": title_pt, "en": title_en},
        "cap": {"pt": cap_pt, "en": cap_en},
        "file": file,
    }


SPECS = [
    C("Fundamentos de Linux", 0, "cols", "Tudo é arquivo", "Everything is a file",
      [("Processo", ["nginx", "bash"]), ("VFS", ["kernel"]), ("Arquivo", ["/etc", "/dev", "/proc"])],
      [("Process", ["nginx", "bash"]), ("VFS", ["kernel"]), ("File", ["/etc", "/dev", "/proc"])],
      "O processo não abre um disco ou a rede. Ele abre um arquivo, e o kernel traduz.",
      "The process does not open a disk or the network. It opens a file, and the kernel translates.",
      "d-linux-files"),
    C("Fundamentos de Linux", 2, "cols", "Permissão rwx", "rwx permission",
      [("Dono", ["r w x"]), ("Grupo", ["r w x"]), ("Outros", ["r w x"])],
      [("Owner", ["r w x"]), ("Group", ["r w x"]), ("Others", ["r w x"])],
      "Cada arquivo carrega três trincas. O acesso efetivo é a trinca que descreve você.",
      "Every file carries three triples. The access you get is the triple that describes you.",
      "d-linux-rwx"),
    C("Redes de Computadores", 0, "cols", "Quatro camadas", "Four layers",
      [("Aplicação", ["HTTP", "DNS"]), ("Transporte", ["TCP", "UDP"]), ("Internet", ["IP"]), ("Enlace", ["Ethernet"])],
      [("Application", ["HTTP", "DNS"]), ("Transport", ["TCP", "UDP"]), ("Internet", ["IP"]), ("Link", ["Ethernet"])],
      "O pacote desce a pilha na origem e sobe na chegada. Cada camada só fala com a vizinha.",
      "The packet goes down the stack at the source and up at the destination. Each layer only talks to its neighbor.",
      "d-tcp-layers"),
    C("Redes de Computadores", 2, "cycle", "Aperto de mão TCP", "TCP handshake",
      ["Cliente SYN", "Servidor", "SYN-ACK", "Cliente ACK"],
      ["Client SYN", "Server", "SYN-ACK", "Client ACK"],
      "TCP confirma os dois lados antes de entregar byte. UDP não faz esse ciclo.",
      "TCP confirms both sides before delivering a byte. UDP does not run this cycle.",
      "d-tcp-handshake"),
    C("Bash/Shell Scripting", 0, "cols", "Cabeçalho seguro", "Safe header",
      [("set -euo pipefail", ["opções"]), ("comando falha", ["exit ≠ 0"]), ("script para", ["não segue"])],
      [("set -euo pipefail", ["options"]), ("command fails", ["exit ≠ 0"]), ("script stops", ["does not continue"])],
      "Sem o cabeçalho, o erro vira passo seguinte. Com ele, a falha interrompe o script.",
      "Without the header, an error becomes the next step. With it, the failure stops the script.",
      "d-bash-header"),
    C("Bash/Shell Scripting", 2, "cols", "Controle de fluxo", "Control flow",
      [("if", ["condição"]), ("for", ["lista"]), ("case", ["padrão"])],
      [("if", ["condition"]), ("for", ["list"]), ("case", ["pattern"])],
      "O script deixa de ser uma lista cega: cada estrutura decide se o próximo comando roda.",
      "The script stops being a blind list: each structure decides whether the next command runs.",
      "d-bash-flow"),
    C("SSH & Chaves Criptográficas", 0, "cols", "SSH com chave", "SSH with a key",
      [("Cliente", ["chave privada"]), ("Desafio", ["assinatura"]), ("Servidor", ["authorized_keys"]), ("Sessão", ["AES"])],
      [("Client", ["private key"]), ("Challenge", ["signature"]), ("Server", ["authorized_keys"]), ("Session", ["AES"])],
      "A privada assina e não sai da máquina. A pública no servidor só confere. O tráfego depois é simétrico.",
      "The private key signs and never leaves the machine. The public key on the server only verifies. Traffic after that is symmetric.",
      "d-ssh-flow"),
    C("SSH & Chaves Criptográficas", 2, "cols", "ssh-agent", "ssh-agent",
      [("Disco", ["chave cifrada"]), ("agent", ["memória"]), ("ssh", ["usa o agent"])],
      [("Disk", ["encrypted key"]), ("agent", ["memory"]), ("ssh", ["uses the agent"])],
      "A passphrase abre a chave uma vez. O agent segura a chave aberta pelo tempo que você mandou.",
      "The passphrase unlocks the key once. The agent holds the unlocked key for as long as you asked.",
      "d-ssh-agent"),
    C("Princípio do Privilégio Mínimo (PoLP)", 0, "cols", "Privilégio mínimo", "Least privilege",
      [("Identidade", ["user", "role"]), ("Permissão", ["só o necessário"]), ("Recurso", ["o alvo"])],
      [("Identity", ["user", "role"]), ("Permission", ["only what is needed"]), ("Resource", ["the target"])],
      "O caminho certo tem uma permissão no meio, não um atalho de administrador até o recurso.",
      "The right path has one permission in the middle, not an administrator shortcut to the resource.",
      "d-polp"),
    C("Princípio do Privilégio Mínimo (PoLP)", 2, "cols", "Hardening do serviço", "Service hardening",
      [("systemd", ["User="]), ("filesystem", ["ProtectSystem"]), ("rede", ["RestrictAddress"])],
      [("systemd", ["User="]), ("filesystem", ["ProtectSystem"]), ("network", ["RestrictAddress"])],
      "O serviço já nasce sem o que não usa. Cada diretiva fecha um lado: usuário, disco, rede.",
      "The service starts without what it does not use. Each directive closes one side: user, disk, network.",
      "d-polp-systemd"),
    C("Firewall Básico", 0, "cols", "Caminho do pacote", "Packet path",
      [("Pacote", ["chega"]), ("netfilter", ["tabelas"]), ("filter", ["regras"]), ("Decisão", ["ACCEPT", "DROP"])],
      [("Packet", ["arrives"]), ("netfilter", ["tables"]), ("filter", ["rules"]), ("Decision", ["ACCEPT", "DROP"])],
      "O firewall do Linux é este caminho dentro do kernel. A regra não casa, o pacote não segue.",
      "The Linux firewall is this path inside the kernel. If the rule does not match, the packet does not continue.",
      "d-netfilter"),
    C("Firewall Básico", 2, "cols", "UFW", "UFW",
      [("default deny", ["entrada"]), ("allow 22", ["SSH"]), ("allow 443", ["HTTPS"])],
      [("default deny", ["incoming"]), ("allow 22", ["SSH"]), ("allow 443", ["HTTPS"])],
      "UFW só escreve regras no netfilter. Primeiro fecha, depois abre o que o serviço precisa.",
      "UFW only writes rules into netfilter. First it closes, then it opens what the service needs.",
      "d-ufw"),
    C("Web Servers (Nginx/Apache)", 0, "cols", "TLS na borda", "TLS at the edge",
      [("Cliente", ["HTTPS"]), ("Nginx", ["termina TLS"]), ("App", ["HTTP interno"])],
      [("Client", ["HTTPS"]), ("Nginx", ["terminates TLS"]), ("App", ["internal HTTP"])],
      "O certificado e o HTTP/2 ficam no proxy. A aplicação recebe o pedido já aberto.",
      "The certificate and HTTP/2 stay on the proxy. The application receives the request already opened.",
      "d-tls-edge"),
    C("Web Servers (Nginx/Apache)", 2, "cols", "Headers de segurança", "Security headers",
      [("Resposta", ["Nginx"]), ("HSTS", ["HTTPS só"]), ("CSP", ["origem do script"])],
      [("Response", ["Nginx"]), ("HSTS", ["HTTPS only"]), ("CSP", ["script origin"])],
      "O header sai na borda, em toda resposta. A aplicação não precisa lembrar de um por um.",
      "The header leaves at the edge, on every response. The application does not have to remember each one.",
      "d-headers"),
    C("Gestão de Pacotes e Repositórios", 0, "cols", "Confiança do APT", "APT trust",
      [("Espelho", ["Release"]), ("Assinatura", ["chave"]), ("apt", ["confere"]), ("Pacote", ["instala"])],
      [("Mirror", ["Release"]), ("Signature", ["key"]), ("apt", ["checks"]), ("Package", ["installs"])],
      "O pacote só instala se a assinatura do índice bater com a chave em que o sistema confia.",
      "The package installs only if the index signature matches the key the system trusts.",
      "d-apt"),
    C("Gestão de Pacotes e Repositórios", 2, "cols", "Pin de versão", "Version pin",
      [("Produção", ["pin"]), ("Versão", ["exata"]), ("apt upgrade", ["não pula"])],
      [("Production", ["pin"]), ("Version", ["exact"]), ("apt upgrade", ["does not jump"])],
      "O pin segura a versão que você testou. O upgrade deixa de ser uma roleta.",
      "The pin holds the version you tested. Upgrade stops being a gamble.",
      "d-pin"),
    C("Log Management", 0, "cols", "journald", "journald",
      [("Serviço", ["stdout"]), ("journald", ["grava"]), ("journalctl", ["lê"])],
      [("Service", ["stdout"]), ("journald", ["stores"]), ("journalctl", ["reads"])],
      "O serviço escreve no journal. O journalctl só consulta o que esta máquina já guardou.",
      "The service writes to the journal. journalctl only queries what this machine already stored.",
      "d-journal"),
    C("Log Management", 2, "cols", "Um pedido, vários logs", "One request, many logs",
      [("Request ID", ["nasce"]), ("Serviço A", ["mesmo id"]), ("Serviço B", ["mesmo id"])],
      [("Request ID", ["is born"]), ("Service A", ["same id"]), ("Service B", ["same id"])],
      "O identificador cola as linhas. Sem ele, cada serviço conta uma história separada.",
      "The identifier glues the lines together. Without it, each service tells a separate story.",
      "d-trace-id"),
    C("Cultura DevSecOps", 0, "cols", "Um fluxo só", "One flow",
      [("Dev", ["código"]), ("Sec", ["ameaça"]), ("Ops", ["produção"])],
      [("Dev", ["code"]), ("Sec", ["threat"]), ("Ops", ["production"])],
      "Não são três filas. O mesmo mudança passa por quem escreve, quem ameaça e quem opera.",
      "These are not three queues. The same change passes through who writes, who threats, and who operates.",
      "d-devsecops"),
    C("Cultura DevSecOps", 2, "cols", "STRIDE", "STRIDE",
      [("Spoofing", ["identidade"]), ("Tampering", ["alterar"]), ("Info leak", ["vazar"]), ("DoS / Elevation", ["negar", "subir"])],
      [("Spoofing", ["identity"]), ("Tampering", ["change"]), ("Info leak", ["leak"]), ("DoS / Elevation", ["deny", "raise"])],
      "STRIDE é uma lista curta para não esquecer classe de ameaça. Cada caixa é uma pergunta.",
      "STRIDE is a short list so you do not forget a threat class. Each box is a question.",
      "d-stride"),
    C("Virtualização vs. Cloud", 0, "cols", "Do hardware à VM", "From hardware to VM",
      [("Hardware", ["CPU", "RAM"]), ("Hypervisor", ["fatia"]), ("VM", ["guest"])],
      [("Hardware", ["CPU", "RAM"]), ("Hypervisor", ["slices"]), ("VM", ["guest"])],
      "A máquina física continua uma. O hypervisor entrega várias máquinas virtuais em cima dela.",
      "The physical machine is still one. The hypervisor delivers several virtual machines on top of it.",
      "d-vm"),
    C("Virtualização vs. Cloud", 2, "cols", "O que a nuvem acrescenta", "What the cloud adds",
      [("VM", ["já existia"]), ("API", ["self-service"]), ("Conta", ["região", "IAM"])],
      [("VM", ["already existed"]), ("API", ["self-service"]), ("Account", ["region", "IAM"])],
      "Nuvem não é a VM. É a API que cria a VM, cobra e aplica identidade sem abrir chamado.",
      "Cloud is not the VM. It is the API that creates the VM, bills it, and applies identity without a ticket.",
      "d-cloud-api"),
    C("Shared Responsibility Model", 0, "cols", "Quem opera o quê", "Who operates what",
      [("IaaS", ["você: SO e app"]), ("PaaS", ["você: app"]), ("SaaS", ["você: dados e acesso"])],
      [("IaaS", ["you: OS and app"]), ("PaaS", ["you: app"]), ("SaaS", ["you: data and access"])],
      "A linha sobe com o serviço. O que resta para você é o que o provedor não assumiu.",
      "The line moves up with the service. What remains for you is what the provider did not take.",
      "d-shared"),
    C("Shared Responsibility Model", 2, "fanout", "O mesmo dado, donos diferentes", "Same data, different owners",
      "Dado do cliente", ["Criptografia", "IAM", "Backup"],
      "Customer data", ["Encryption", "IAM", "Backup"],
      "Mesmo num SaaS, identidade, cifra e cópia do dado continuam pergunta sua.",
      "Even on SaaS, identity, encryption, and the copy of the data are still your question.",
      "d-shared-data"),
    C("IAM (Identity and Access Management)", 0, "cols", "Humano e máquina", "Human and machine",
      [("Humano", ["usuário"]), ("Policy", ["allow"]), ("Recurso", ["API"]) , ("Máquina", ["role"])],
      [("Human", ["user"]), ("Policy", ["allow"]), ("Resource", ["API"]), ("Machine", ["role"])],
      "Os dois chegam no mesmo recurso, por policies. A máquina não usa a senha da pessoa.",
      "Both reach the same resource, through policies. The machine does not use the person's password.",
      "d-iam"),
    C("IAM (Identity and Access Management)", 2, "cols", "A decisão", "The decision",
      [("Pedido", ["quem"]), ("Policy", ["o quê"]), ("Efeito", ["allow", "deny"])],
      [("Request", ["who"]), ("Policy", ["what"]), ("Effect", ["allow", "deny"])],
      "O IAM não adivinha. Junta identidade e policy e devolve allow ou deny.",
      "IAM does not guess. It joins identity and policy and returns allow or deny.",
      "d-iam-eval"),
    C("VPC & Subnets", 0, "cols", "Anatomia da VPC", "VPC anatomy",
      [("VPC", ["sua rede"]), ("Subnet", ["fatia"]), ("Rota", ["para onde"]), ("IGW / NAT", ["saída"])],
      [("VPC", ["your network"]), ("Subnet", ["slice"]), ("Route", ["where to"]), ("IGW / NAT", ["exit"])],
      "A VPC é o terreno. Subnet, rota e o portão de saída dizem se o pacote fica dentro ou sai.",
      "The VPC is the grounds. Subnet, route, and the exit gate say whether the packet stays in or leaves.",
      "d-vpc"),
    C("VPC & Subnets", 2, "cols", "Pública e privada", "Public and private",
      [("IGW", ["internet"]), ("Subnet pública", ["IP público"]), ("Subnet privada", ["só NAT"])],
      [("IGW", ["internet"]), ("Public subnet", ["public IP"]), ("Private subnet", ["NAT only"])],
      "Pública conversa com a internet. Privada sai por NAT e não recebe conexão nova de fora.",
      "Public talks to the internet. Private leaves through NAT and does not accept a new connection from outside.",
      "d-subnets"),
    C("Security Groups & ACLs", 0, "cols", "Security group", "Security group",
      [("Cliente", ["origem"]), ("SG", ["stateful"]), ("ENI", ["a interface"]), ("App", ["porta"])],
      [("Client", ["source"]), ("SG", ["stateful"]), ("ENI", ["the interface"]), ("App", ["port"])],
      "O SG lembra quem entrou. A resposta desse fluxo volta; o resto da rede continua fechado.",
      "The SG remembers who came in. That flow's reply returns; the rest of the network stays closed.",
      "d-sg"),
    C("Security Groups & ACLs", 2, "cols", "Cadeia de SGs", "SG chain",
      [("SG web", ["443"]), ("SG app", ["só o web"]), ("SG db", ["só o app"])],
      [("SG web", ["443"]), ("SG app", ["web only"]), ("SG db", ["app only"])],
      "Cada grupo cita o anterior. O banco não abre para a internet, só para o SG da aplicação.",
      "Each group cites the previous one. The database does not open to the internet, only to the app SG.",
      "d-sg-chain"),
    C("Object Storage (S3)", 0, "cols", "Objeto, não arquivo", "Object, not a file",
      [("Bucket", ["o balde"]), ("Chave", ["o nome"]), ("Objeto", ["os bytes"])],
      [("Bucket", ["the bucket"]), ("Key", ["the name"]), ("Object", ["the bytes"])],
      "Não há pasta nem rename parcial. Há um balde, uma chave e o objeto inteiro.",
      "There is no folder and no partial rename. There is a bucket, a key, and the whole object.",
      "d-s3"),
    C("Object Storage (S3)", 2, "cols", "Quem pode ler", "Who can read",
      [("Block public", ["trava"]), ("Bucket policy", ["quem"]), ("IAM", ["o principal"])],
      [("Block public", ["lock"]), ("Bucket policy", ["who"]), ("IAM", ["the principal"])],
      "O objeto não é público por existir. As três camadas precisam concordar em deixar ler.",
      "The object is not public just because it exists. The three layers have to agree to allow a read.",
      "d-s3-policy"),
    C("Criptografia em Repouso e Trânsito", 0, "cols", "Onde a cifra atua", "Where encryption acts",
      [("Em repouso", ["disco", "backup"]), ("Em trânsito", ["TLS"]), ("Em uso", ["RAM"])],
      [("At rest", ["disk", "backup"]), ("In transit", ["TLS"]), ("In use", ["RAM"])],
      "Cofre e TLS não protegem o dado enquanto ele está aberto na memória.",
      "The safe and TLS do not protect the data while it is open in memory.",
      "d-crypto"),
    C("Criptografia em Repouso e Trânsito", 2, "cols", "O que ainda serve", "What still holds",
      [("TLS 1.3", ["trânsito"]), ("AES-GCM", ["repouso"]), ("MD5 / SHA-1", ["não usar"])],
      [("TLS 1.3", ["transit"]), ("AES-GCM", ["at rest"]), ("MD5 / SHA-1", ["do not use"])],
      "Algoritmo velho no meio do caminho anula o cofre novo.",
      "An old algorithm in the middle cancels the new safe.",
      "d-crypto-algos"),
    C("Monitoramento Básico (CloudWatch/Monitor)", 0, "cols", "Quatro sinais", "Four signals",
      [("Latência", ["tempo"]), ("Tráfego", ["volume"]), ("Erros", ["falha"]), ("Saturação", ["cheio"])],
      [("Latency", ["time"]), ("Traffic", ["volume"]), ("Errors", ["failure"]), ("Saturation", ["full"])],
      "Quatro ponteiros dizem se o serviço está bem. O resto do painel é detalhe.",
      "Four needles say whether the service is fine. The rest of the dashboard is detail.",
      "d-golden"),
    C("Monitoramento Básico (CloudWatch/Monitor)", 2, "cols", "Error budget", "Error budget",
      [("SLO", ["meta"]), ("Budget", ["folga"]), ("Burn", ["velocidade"]), ("Alerta", ["página"])],
      [("SLO", ["target"]), ("Budget", ["slack"]), ("Burn", ["speed"]), ("Alert", ["page"])],
      "O alerta dispara pela velocidade com que o budget acaba, não por um pico isolado.",
      "The alert fires from how fast the budget runs out, not from an isolated spike.",
      "d-burn"),
    C("Backup & Disaster Recovery", 0, "cols", "RPO e RTO", "RPO and RTO",
      [("Dado vivo", ["agora"]), ("RPO", ["quanto perde"]), ("Cópia", ["o backup"]), ("RTO", ["quanto demora"])],
      [("Live data", ["now"]), ("RPO", ["how much is lost"]), ("Copy", ["the backup"]), ("RTO", ["how long"])],
      "RPO é o pedaço de tempo sem cópia. RTO é o tempo até essa cópia voltar a atender.",
      "RPO is the stretch of time with no copy. RTO is the time until that copy serves again.",
      "d-rpo"),
    C("Backup & Disaster Recovery", 2, "cols", "Estratégia de DR", "DR strategy",
      [("Backup", ["barato", "lento"]), ("Standby", ["morno"]), ("Ativo-ativo", ["caro", "rápido"])],
      [("Backup", ["cheap", "slow"]), ("Standby", ["warm"]), ("Active-active", ["costly", "fast"])],
      "Quanto menor o RTO, mais a cópia precisa estar acordada. O preço sobe junto.",
      "The smaller the RTO, the more awake the copy must be. The price rises with it.",
      "d-dr"),
    C("FinOps Inicial", 0, "cols", "Do clique à fatura", "From click to bill",
      [("Tag", ["quem"]), ("Recurso", ["o quê"]), ("Custo", ["a fatura"]), ("Decisão", ["corta ou escala"])],
      [("Tag", ["who"]), ("Resource", ["what"]), ("Cost", ["the bill"]), ("Decision", ["cut or scale"])],
      "Sem tag, a fatura é um número só. Com tag, dá para decidir o que fica ligado.",
      "Without a tag, the bill is one number. With a tag, you can decide what stays on.",
      "d-finops"),
    C("FinOps Inicial", 2, "cols", "Como se paga", "How you pay",
      [("On-demand", ["flexível"]), ("Reserved", ["compromisso"]), ("Spot", ["pode morrer"])],
      [("On-demand", ["flexible"]), ("Reserved", ["commitment"]), ("Spot", ["can die"])],
      "O desconto troca flexibilidade. Spot só cabe em carga que pode parar.",
      "The discount trades flexibility. Spot only fits a workload that can stop.",
      "d-pricing"),
    C("Versionamento com Git", 0, "cols", "O que o Git guarda", "What Git stores",
      [("Working tree", ["arquivos"]), ("Commit", ["snapshot"]), ("Hash", ["o endereço"])],
      [("Working tree", ["files"]), ("Commit", ["snapshot"]), ("Hash", ["the address"])],
      "Cada commit é um retrato inteiro, endereçado pelo hash. Não é um delta solto.",
      "Each commit is a whole snapshot, addressed by the hash. It is not a loose delta.",
      "d-git"),
    C("Versionamento com Git", 2, "cols", "Branch protegida", "Protected branch",
      [("PR", ["proposta"]), ("Review", ["alguém vê"]), ("CI", ["verde"]), ("main", ["merge"])],
      [("PR", ["proposal"]), ("Review", ["someone looks"]), ("CI", ["green"]), ("main", ["merge"])],
      "A main não recebe push direto. O commit entra por PR, review e CI.",
      "Main does not take a direct push. The commit enters through PR, review, and CI.",
      "d-git-pr"),
    C("Infraestrutura como Código (Terraform)", 0, "cols", "Código vira infra", "Code becomes infra",
      [("Código", ["o desejado"]), ("Plan", ["o diff"]), ("Apply", ["age"]), ("State", ["o real"])],
      [("Code", ["desired"]), ("Plan", ["the diff"]), ("Apply", ["acts"]), ("State", ["actual"])],
      "O plan mostra a diferença antes. O state é a memória do que já existe.",
      "The plan shows the difference first. State is the memory of what already exists.",
      "d-terraform"),
    C("Infraestrutura como Código (Terraform)", 2, "cycle", "init, plan, apply", "init, plan, apply",
      ["init", "plan", "review", "apply"],
      ["init", "plan", "review", "apply"],
      "Apply sem plan revisado é mudança no escuro. O ciclo volta no próximo commit.",
      "Apply without a reviewed plan is a change in the dark. The cycle returns on the next commit.",
      "d-tf-loop"),
    C("Gestão de Configuração (Ansible)", 0, "cols", "Sem agente", "No agent",
      [("Control node", ["playbook"]), ("SSH", ["entra"]), ("Host", ["Python"]), ("Estado", ["o desejado"])],
      [("Control node", ["playbook"]), ("SSH", ["enters"]), ("Host", ["Python"]), ("State", ["desired"])],
      "Não há agente instalado. O control node entra por SSH e aplica o estado.",
      "There is no agent installed. The control node comes in over SSH and applies the state.",
      "d-ansible"),
    C("Gestão de Configuração (Ansible)", 2, "cycle", "Idempotência", "Idempotency",
      ["Estado desejado", "Host", "Já está?", "Não muda"],
      ["Desired state", "Host", "Already there?", "No change"],
      "Rodar de novo não empilha efeito. Se o host já está no estado, a task não mexe.",
      "Running again does not stack an effect. If the host is already in the state, the task does not touch it.",
      "d-ansible-idem"),
    C("Secret Management", 0, "cols", "Tipos de segredo", "Secret types",
      [("Senha", ["pessoa"]), ("Chave de API", ["máquina"]), ("Certificado", ["serviço"])],
      [("Password", ["person"]), ("API key", ["machine"]), ("Certificate", ["service"])],
      "Não é tudo 'a senha'. Cada tipo tem dono, rotação e lugar diferentes.",
      "It is not all 'the password'. Each type has a different owner, rotation, and place.",
      "d-secret-types"),
    C("Secret Management", 2, "cols", "Caminho do segredo", "Secret path",
      [("App", ["pede"]), ("Cofre", ["entrega"]), ("Memória", ["usa"]), ("Código", ["não guarda"])],
      [("App", ["asks"]), ("Vault", ["delivers"]), ("Memory", ["uses"]), ("Code", ["does not store"])],
      "O segredo nasce no cofre e morre na memória do processo. O repositório fica de fora.",
      "The secret is born in the vault and dies in the process memory. The repository stays out.",
      "d-vault"),
    C("CI/CD Básico", 0, "cols", "CI e CD", "CI and CD",
      [("Commit", ["entra"]), ("CI", ["build", "teste"]), ("Artefato", ["pronto"]), ("CD", ["deploy"])],
      [("Commit", ["enters"]), ("CI", ["build", "test"]), ("Artifact", ["ready"]), ("CD", ["deploy"])],
      "CI prova o commit. CD leva o artefato. Entrega contínua ainda pode esperar um humano.",
      "CI proves the commit. CD carries the artifact. Continuous delivery can still wait for a human.",
      "d-cicd"),
    C("CI/CD Básico", 2, "cols", "Pipeline", "Pipeline",
      [("push", ["branch"]), ("lint + test", ["CI"]), ("imagem", ["registry"]), ("deploy", ["ambiente"])],
      [("push", ["branch"]), ("lint + test", ["CI"]), ("image", ["registry"]), ("deploy", ["environment"])],
      "O YAML do Actions é esse caminho. Cada caixa é um job que só roda se a anterior passou.",
      "The Actions YAML is this path. Each box is a job that runs only if the previous one passed.",
      "d-actions"),
    C("Linting de Código e IaC", 0, "cols", "O que o linter faz", "What a linter does",
      [("Código", ["entra"]), ("Regra", ["estilo", "erro"]), ("Achado", ["antes do review"])],
      [("Code", ["enters"]), ("Rule", ["style", "error"]), ("Finding", ["before review"])],
      "O linter tira o fiapo mecânico. O review humano fica com o que a regra não alcança.",
      "The linter lifts the mechanical fluff. Human review keeps what the rule cannot reach.",
      "d-lint"),
    C("Linting de Código e IaC", 2, "cols", "Linter de infra", "Infra linter",
      [("Terraform", ["fmt / validate"]), ("Policy", ["checkov"]), ("CI", ["barra o merge"])],
      [("Terraform", ["fmt / validate"]), ("Policy", ["checkov"]), ("CI", ["blocks the merge"])],
      "Infra também tem fiapo: formato, validate e policy rodam antes do apply.",
      "Infra has fluff too: format, validate, and policy run before apply.",
      "d-lint-iac"),
    C("SAST", 0, "cols", "SAST por dentro", "SAST inside",
      [("Fonte", ["não roda"]), ("AST", ["a árvore"]), ("Regra", ["o padrão"]), ("Achado", ["a linha"])],
      [("Source", ["does not run"]), ("AST", ["the tree"]), ("Rule", ["the pattern"]), ("Finding", ["the line"])],
      "O SAST lê o código parado. A regra casa com a árvore, não com o programa em execução.",
      "SAST reads the code standing still. The rule matches the tree, not the running program.",
      "d-sast"),
    C("SAST", 2, "cols", "Onde roda", "Where it runs",
      [("PR", ["o diff"]), ("SAST", ["semver open"]), ("CI", ["falha o check"])],
      [("PR", ["the diff"]), ("SAST", ["open source"]), ("CI", ["fails the check"])],
      "A ferramenta open source no CI olha o diff do PR. O achado volta antes do merge.",
      "The open-source tool in CI looks at the PR diff. The finding comes back before the merge.",
      "d-sast-ci"),
    C("SCA", 0, "cols", "Do que o app é feito", "What the app is made of",
      [("App", ["seu código"]), ("Dependências", ["as peças"]), ("SBOM", ["a lista"]), ("CVE", ["a peça ruim"])],
      [("App", ["your code"]), ("Dependencies", ["the parts"]), ("SBOM", ["the list"]), ("CVE", ["the bad part"])],
      "SCA não lê a sua lógica. Lê a lista de peças e marca a que tem falha conhecida.",
      "SCA does not read your logic. It reads the parts list and marks the one with a known flaw.",
      "d-sca"),
    C("SCA", 2, "cols", "Ferramenta", "Tool",
      [("Lockfile", ["versões"]), ("Scanner", ["consulta CVE"]), ("PR", ["o aviso"])],
      [("Lockfile", ["versions"]), ("Scanner", ["checks CVE"]), ("PR", ["the warning"])],
      "Sem lockfile a lista muda a cada build. O scanner precisa da versão exata.",
      "Without a lockfile the list changes every build. The scanner needs the exact version.",
      "d-sca-tool"),
    C("Code Review", 0, "cols", "Um PR", "One PR",
      [("Autor", ["o diff"]), ("Revisor", ["lê"]), ("CI", ["verde"]), ("Merge", ["entra"])],
      [("Author", ["the diff"]), ("Reviewer", ["reads"]), ("CI", ["green"]), ("Merge", ["lands"])],
      "Review é duas pessoas no mesmo diff, com o CI já verde, antes do merge.",
      "Review is two people on the same diff, with CI already green, before the merge.",
      "d-review"),
    C("Code Review", 2, "fanout", "CODEOWNERS", "CODEOWNERS",
      "PR", ["Dono do módulo", "Sec do auth", "Ops do deploy"],
      "PR", ["Module owner", "Auth security", "Deploy ops"],
      "O arquivo diz quem é obrigatório. O PR não entra sem o dono daquela pasta.",
      "The file says who is required. The PR does not land without the owner of that folder.",
      "d-codeowners"),
    C("Artifact Repositories", 0, "cols", "O que o registry guarda", "What the registry stores",
      [("Imagem", ["container"]), ("Chart", ["Helm"]), ("Pacote", ["lib"])],
      [("Image", ["container"]), ("Chart", ["Helm"]), ("Package", ["lib"])],
      "O registry não é pasta solta. É o lugar versionado de onde o deploy puxa o artefato.",
      "The registry is not a loose folder. It is the versioned place deploy pulls the artifact from.",
      "d-registry-types"),
    C("Artifact Repositories", 2, "cols", "Quem empurra e quem puxa", "Who pushes and who pulls",
      [("CI", ["push"]), ("Registry", ["guarda"]), ("RBAC", ["separa"]), ("Prod", ["pull"])],
      [("CI", ["push"]), ("Registry", ["stores"]), ("RBAC", ["separates"]), ("Prod", ["pull"])],
      "Quem publica não é quem roda em produção. O RBAC separa os dois papéis.",
      "Whoever publishes is not whoever runs in production. RBAC separates the two roles.",
      "d-registry-rbac"),
    C("Docker Fundamentals", 0, "cols", "Container por dentro", "Container inside",
      [("Processo", ["o app"]), ("Namespace", ["isola"]), ("cgroup", ["limita"]), ("Kernel", ["o do host"])],
      [("Process", ["the app"]), ("Namespace", ["isolates"]), ("cgroup", ["limits"]), ("Kernel", ["the host's"])],
      "Não há segunda máquina. Há um processo no kernel do host, isolado e limitado.",
      "There is no second machine. There is a process on the host kernel, isolated and limited.",
      "d-docker"),
    C("Docker Fundamentals", 2, "cols", "Cache do build", "Build cache",
      [("Instrução", ["uma camada"]), ("Cache", ["se não mudou"]), ("COPY cedo", ["invalida tudo"])],
      [("Instruction", ["one layer"]), ("Cache", ["if unchanged"]), ("Early COPY", ["invalidates all"])],
      "A ordem vira camadas. Mudar um arquivo copiado no topo refaz tudo que vem depois.",
      "Order becomes layers. Changing a file copied at the top rebuilds everything after it.",
      "d-docker-cache"),
    C("Segurança de Imagens", 0, "cols", "Imagem mínima", "Minimal image",
      [("Base", ["poucos bytes"]), ("App", ["só o necessário"]), ("Resto", ["não entra"])],
      [("Base", ["few bytes"]), ("App", ["only what is needed"]), ("Rest", ["stays out"])],
      "Cada pacote a mais é superfície. A imagem leva o app, não uma distro inteira.",
      "Every extra package is attack surface. The image carries the app, not a whole distro.",
      "d-minimal"),
    C("Segurança de Imagens", 2, "cols", "Não-root", "Non-root",
      [("USER", ["uid comum"]), ("Capability", ["as que faltam"]), ("Root", ["fora"])],
      [("USER", ["ordinary uid"]), ("Capability", ["the ones missing"]), ("Root", ["out"])],
      "O processo da imagem não é root. O que falta de capability não pode ser abusado.",
      "The image process is not root. The capability it lacks cannot be abused.",
      "d-nonroot"),
    C("Container Registry", 0, "cols", "Onde a imagem mora", "Where the image lives",
      [("Build", ["CI"]), ("Registry", ["o catálogo"]), ("Pull", ["cluster"])],
      [("Build", ["CI"]), ("Registry", ["the catalog"]), ("Pull", ["cluster"])],
      "O cluster não guarda a imagem no git. Ele puxa do registry na hora de subir.",
      "The cluster does not store the image in git. It pulls from the registry when it starts.",
      "d-registry"),
    C("Container Registry", 2, "cols", "Tag não é versão", "A tag is not a version",
      [("Tag", ["nome móvel"]), ("Digest", ["o hash"]), ("Prod", ["prende o digest"])],
      [("Tag", ["movable name"]), ("Digest", ["the hash"]), ("Prod", ["pins the digest"])],
      "A mesma tag pode apontar para outro conteúdo amanhã. Produção prende o digest.",
      "The same tag can point at different content tomorrow. Production pins the digest.",
      "d-digest"),
    C("Orquestração Simples", 0, "fanout", "Um Compose", "One Compose",
      "compose.yaml", ["app", "db", "cache"],
      "compose.yaml", ["app", "db", "cache"],
      "Um arquivo declara os containers. O Compose sobe o conjunto, não uma peça solta.",
      "One file declares the containers. Compose brings up the set, not a loose piece.",
      "d-compose"),
    C("Orquestração Simples", 2, "cols", "Segredo no Compose", "Secret in Compose",
      [(".env", ["local"]), ("variável", ["no container"]), ("cofre", ["quando cresce"])],
      [(".env", ["local"]), ("variable", ["in the container"]), ("vault", ["when it grows"])],
      "O .env serve na máquina de quem desenvolve. Segredo de verdade não fica nesse arquivo.",
      "The .env file serves on the developer's machine. A real secret does not stay in that file.",
      "d-compose-env"),
    C("Software Bill of Materials (SBOM)", 0, "cols", "SBOM", "SBOM",
      [("Imagem", ["o artefato"]), ("syft", ["lê"]), ("SBOM", ["a lista"]), ("CVE", ["Log4Shell"])],
      [("Image", ["the artifact"]), ("syft", ["reads"]), ("SBOM", ["the list"]), ("CVE", ["Log4Shell"])],
      "Sem a lista, achar se o Log4j está aí é abrir no escuro. O SBOM é a lista.",
      "Without the list, finding whether Log4j is in there is opening it in the dark. The SBOM is the list.",
      "d-sbom"),
    C("Software Bill of Materials (SBOM)", 2, "cols", "Geração automática", "Automatic generation",
      [("CI", ["no build"]), ("SBOM", ["sai junto"]), ("Arquivo manual", ["não"])],
      [("CI", ["at build"]), ("SBOM", ["ships along"]), ("Hand-written file", ["no"])],
      "Lista feita à mão mente no commit seguinte. Quem gera é o pipeline, toda vez.",
      "A hand-written list lies on the next commit. The pipeline generates it, every time.",
      "d-sbom-ci"),
    C("Internal Developer Platforms (IDP)", 0, "cols", "Por que a IDP existe", "Why an IDP exists",
      [("Time", ["pede ambiente"]), ("Portal", ["um caminho"]), ("Plataforma", ["entrega"])],
      [("Team", ["asks for an environment"]), ("Portal", ["one path"]), ("Platform", ["delivers"])],
      "Sem portal, cada time monta o próprio caminho. A IDP é o caminho único.",
      "Without a portal, every team builds its own path. The IDP is the single path.",
      "d-idp"),
    C("Internal Developer Platforms (IDP)", 2, "cols", "Backstage", "Backstage",
      [("Catálogo", ["os serviços"]), ("Template", ["o padrão"]), ("Time", ["cria pelo portal"])],
      [("Catalog", ["the services"]), ("Template", ["the standard"]), ("Team", ["creates via the portal"])],
      "O template carrega o padrão. O time não copia um YAML velho de outro repositório.",
      "The template carries the standard. The team does not copy an old YAML from another repository.",
      "d-backstage"),
    C("Policy as Code (PaC)", 0, "fanout", "A mesma regra", "The same rule",
      "Policy", ["PR", "CI", "Admission", "Runtime"],
      "Policy", ["PR", "CI", "Admission", "Runtime"],
      "Uma regra, quatro portas. O que o PR barra não precisa ser redescoberto no cluster.",
      "One rule, four doors. What the PR blocks does not have to be rediscovered on the cluster.",
      "d-policy"),
    C("Policy as Code (PaC)", 2, "cols", "Conftest", "Conftest",
      [("YAML / TF", ["o arquivo"]), ("Rego", ["a regra"]), ("conftest", ["fora do cluster"])],
      [("YAML / TF", ["the file"]), ("Rego", ["the rule"]), ("conftest", ["off cluster"])],
      "A mesma engine do OPA roda no CI, em cima do arquivo, antes de existir um cluster.",
      "The same OPA engine runs in CI, on the file, before a cluster exists.",
      "d-conftest"),
    C("DAST inicial", 0, "cols", "Quatro testes", "Four tests",
      [("SAST", ["código parado"]), ("SCA", ["dependência"]), ("DAST", ["app no ar"]), ("Pentest", ["pessoa"])],
      [("SAST", ["code at rest"]), ("SCA", ["dependency"]), ("DAST", ["app running"]), ("Pentest", ["a person"])],
      "DAST é a caixa do meio-fim: o app já está de pé e o teste vem de fora.",
      "DAST is the later box: the app is already up and the test comes from outside.",
      "d-dast"),
    C("DAST inicial", 2, "cols", "Burp no fluxo", "Burp in the flow",
      [("Browser", ["o pedido"]), ("Burp", ["intercepta"]), ("App", ["responde"])],
      [("Browser", ["the request"]), ("Burp", ["intercepts"]), ("App", ["responds"])],
      "O proxy vê e altera o pedido antes da aplicação. É o teste de fora, pedido a pedido.",
      "The proxy sees and changes the request before the application. It is the outside test, request by request.",
      "d-burp"),
    C("API Security", 0, "cols", "Quem chama", "Who is calling",
      [("Cliente", ["token"]), ("API", ["confere"]), ("Handler", ["já autenticado"])],
      [("Client", ["token"]), ("API", ["checks"]), ("Handler", ["already authenticated"])],
      "Autenticar é provar quem chama. O handler não inventa criptografia; ele recebe o principal.",
      "Authentication proves who is calling. The handler does not invent cryptography; it receives the principal.",
      "d-api-auth"),
    C("API Security", 2, "cols", "Schema na porta", "Schema at the door",
      [("Pedido", ["JSON"]), ("Schema", ["rejeita"]), ("Código", ["só o válido"])],
      [("Request", ["JSON"]), ("Schema", ["rejects"]), ("Code", ["only the valid"])],
      "O que não cabe no schema não chega na regra de negócio.",
      "What does not fit the schema never reaches the business rule.",
      "d-api-schema"),
    C("Centralized Logging", 0, "cols", "Da app ao backend", "From app to backend",
      [("App", ["loga"]), ("Agente", ["coleta"]), ("Backend", ["guarda"]), ("Busca", ["investiga"])],
      [("App", ["logs"]), ("Agent", ["collects"]), ("Backend", ["stores"]), ("Search", ["investigates"])],
      "Cada pilha troca o agente e o backend. O caminho é o mesmo: sair da app e parar num lugar só.",
      "Each stack swaps the agent and the backend. The path is the same: leave the app and stop in one place.",
      "d-logs"),
    C("Centralized Logging", 2, "cols", "Coleta", "Collection",
      [("App", ["stdout"]), ("Agente", ["no nó"]), ("Fila", ["aguenta pico"]), ("Índice", ["busca"])],
      [("App", ["stdout"]), ("Agent", ["on the node"]), ("Queue", ["absorbs the spike"]), ("Index", ["search"])],
      "A app não fala com o índice. O agente e a fila seguram o volume.",
      "The app does not talk to the index. The agent and the queue hold the volume.",
      "d-logs-agent"),
    C("Introdução ao Kubernetes (K8s)", 0, "cycle", "Você declara", "You declare",
      ["Spec", "API Server", "Controller", "Estado real"],
      ["Spec", "API Server", "Controller", "Actual state"],
      "Você não manda um comando solto. Declara a spec, e o controller repete o ciclo até o mundo bater.",
      "You do not send a one-off command. You declare the spec, and the controller repeats the cycle until the world matches.",
      "d-k8s-loop"),
    C("Introdução ao Kubernetes (K8s)", 1, "k8s", "Componentes do cluster", "Cluster components",
      None, None,
      "O API Server é a única porta. etcd, scheduler e controllers ficam no control plane; kubelet sobe o pod no worker.",
      "The API Server is the only door. etcd, the scheduler, and the controllers stay on the control plane; the kubelet starts the pod on the worker.",
      "d-k8s-cluster"),
    C("Introdução ao Kubernetes (K8s)", 2, "cols", "Primitivos", "Primitives",
      [("Deployment", ["o desejado"]), ("ReplicaSet", ["quantos"]), ("Pod", ["a unidade"]), ("Container", ["o processo"])],
      [("Deployment", ["desired"]), ("ReplicaSet", ["how many"]), ("Pod", ["the unit"]), ("Container", ["the process"])],
      "O Deployment não roda o processo. Ele garante ReplicaSets, que garantem Pods, que carregam containers.",
      "The Deployment does not run the process. It ensures ReplicaSets, which ensure Pods, which carry containers.",
      "d-k8s-primitives"),
    C("Introdução ao Kubernetes (K8s)", 4, "cols", "Rolling update", "Rolling update",
      [("ReplicaSet v1", ["pods velhos"]), ("Surge", ["sobe o novo"]), ("Ready", ["entra"]), ("v1", ["esvazia"])],
      [("ReplicaSet v1", ["old pods"]), ("Surge", ["starts the new"]), ("Ready", ["joins"]), ("v1", ["drains"])],
      "Não troca tudo de uma vez. Sobe um novo, espera ficar pronto, tira um velho.",
      "It does not swap everything at once. It starts a new one, waits until it is ready, and removes an old one.",
      "d-k8s-roll"),
    C("Introdução ao Kubernetes (K8s)", 5, "fanout", "Service", "Service",
      "ClusterIP", ["Pod A", "Pod B", "Pod C"],
      "ClusterIP", ["Pod A", "Pod B", "Pod C"],
      "O cliente fala com o IP estável do Service. O pod morre, o IP do pod muda, o ClusterIP fica.",
      "The client talks to the Service's stable IP. The pod dies, the pod IP changes, the ClusterIP stays.",
      "d-k8s-svc"),
    C("Introdução ao Kubernetes (K8s)", 6, "fanout", "Ingress", "Ingress",
      "Ingress :443", ["Service web", "Service api", "Service auth"],
      "Ingress :443", ["Service web", "Service api", "Service auth"],
      "Uma porta pública, várias rotas. O Ingress escolhe o Service pelo host ou pelo path.",
      "One public port, many routes. The Ingress picks the Service by host or by path.",
      "d-k8s-ing"),
    C("K8s Hardening", 0, "cols", "O salto do atacante", "The attacker's jump",
      [("Internet", ["a app"]), ("Container", ["breakout"]), ("Nó", ["kubelet"]), ("Cluster", ["API"])],
      [("Internet", ["the app"]), ("Container", ["breakout"]), ("Node", ["kubelet"]), ("Cluster", ["API"])],
      "Cada controle trava um salto. Hardening sem esse caminho vira checklist solta.",
      "Each control stops one jump. Hardening without this path becomes a loose checklist.",
      "d-harden-path"),
    C("K8s Hardening", 2, "cols", "Pod Security", "Pod Security",
      [("Privileged", ["quase tudo"]), ("Baseline", ["o meio"]), ("Restricted", ["o mínimo"])],
      [("Privileged", ["almost all"]), ("Baseline", ["the middle"]), ("Restricted", ["the minimum"])],
      "O namespace escolhe o nível. Restricted recusa o pod que pede privilégio a mais.",
      "The namespace chooses the level. Restricted refuses the pod that asks for extra privilege.",
      "d-pss"),
    C("Network Policies", 0, "cols", "Quem aplica", "Who enforces",
      [("NetworkPolicy", ["o objeto"]), ("API", ["guarda"]), ("CNI", ["aplica no nó"])],
      [("NetworkPolicy", ["the object"]), ("API", ["stores"]), ("CNI", ["enforces on the node"])],
      "O YAML sozinho não filtra pacote. Quem filtra é o CNI, se ele implementar a policy.",
      "The YAML alone does not filter packets. The CNI does, if it implements the policy.",
      "d-netpol"),
    C("Network Policies", 2, "fanout", "Default deny", "Default deny",
      "Namespace fechado", ["DNS", "App", "nada mais"],
      "Closed namespace", ["DNS", "App", "nothing else"],
      "Primeiro nega tudo. Depois abre só DNS e o fluxo da aplicação.",
      "First deny everything. Then open only DNS and the application flow.",
      "d-netpol-deny"),
    C("Admission Controllers", 0, "cols", "Onde o admission entra", "Where admission sits",
      [("Pedido", ["kubectl"]), ("Auth", ["quem"]), ("Admission", ["aceita?"]), ("etcd", ["grava"])],
      [("Request", ["kubectl"]), ("Auth", ["who"]), ("Admission", ["accept?"]), ("etcd", ["stores"])],
      "Auth diz quem é. Admission diz se esse objeto pode existir. Só então o etcd grava.",
      "Auth says who it is. Admission says whether that object may exist. Only then etcd stores it.",
      "d-admission"),
    C("Admission Controllers", 2, "cols", "Engines", "Engines",
      [("Gatekeeper", ["OPA"]), ("Kyverno", ["YAML"]), ("Webhook", ["o seu código"])],
      [("Gatekeeper", ["OPA"]), ("Kyverno", ["YAML"]), ("Webhook", ["your code"])],
      "As três sentam no mesmo ponto da cadeia. Muda a linguagem da regra, não o lugar.",
      "All three sit at the same point in the chain. The rule language changes, not the place.",
      "d-admission-engines"),
    C("Zero Trust Architecture", 0, "cols", "O perímetro quebrou", "The perimeter broke",
      [("Borda", ["não basta"]), ("Rede interna", ["já não é confiável"]), ("Pedido", ["prova de novo"])],
      [("Edge", ["not enough"]), ("Internal network", ["no longer trusted"]), ("Request", ["proves again"])],
      "Estar dentro da rede não autoriza. Cada pedido prova identidade de novo.",
      "Being inside the network does not authorize. Each request proves identity again.",
      "d-zerotrust"),
    C("Zero Trust Architecture", 2, "cycle", "Por requisição", "Per request",
      ["Identidade", "Contexto", "Policy", "Allow"],
      ["Identity", "Context", "Policy", "Allow"],
      "A definição do NIST cabe neste ciclo: nada é confiável só porque o pedido anterior foi.",
      "The NIST definition fits this cycle: nothing is trusted just because the previous request was.",
      "d-zerotrust-req"),
    C("Runtime Security", 0, "cols", "eBPF", "eBPF",
      [("Evento", ["syscall"]), ("Programa", ["eBPF"]), ("Kernel", ["roda sem recompilar"]), ("Alerta", ["sai"])],
      [("Event", ["syscall"]), ("Program", ["eBPF"]), ("Kernel", ["runs without recompile"]), ("Alert", ["leaves"])],
      "O programa observa o kernel enquanto ele roda. Não é módulo que exige reboot.",
      "The program watches the kernel while it runs. It is not a module that requires a reboot.",
      "d-ebpf"),
    C("Runtime Security", 2, "cols", "Tetragon", "Tetragon",
      [("Syscall", ["o fato"]), ("Policy", ["a regra"]), ("Ação", ["mata o processo"])],
      [("Syscall", ["the fact"]), ("Policy", ["the rule"]), ("Action", ["kills the process"])],
      "Alertar chega tarde. A policy no kernel pode encerrar o processo no mesmo evento.",
      "Alerting arrives late. The policy in the kernel can end the process on the same event.",
      "d-tetragon"),
    C("Observabilidade Avançada", 0, "cols", "Três pilares", "Three pillars",
      [("Métrica", ["o agregado"]), ("Log", ["o evento"]), ("Trace", ["o caminho"])],
      [("Metric", ["the aggregate"]), ("Log", ["the event"]), ("Trace", ["the path"])],
      "Um pilar diz o quê, outro diz o detalhe, o terceiro diz por onde passou. Sozinho, cada um mente por omissão.",
      "One pillar says what, another says the detail, the third says the path. Alone, each lies by omission.",
      "d-pillars"),
    C("Observabilidade Avançada", 2, "cols", "OpenTelemetry", "OpenTelemetry",
      [("App", ["SDK"]), ("OTLP", ["o protocolo"]), ("Collector", ["roteia"]), ("Backend", ["troca sem reescrever"])],
      [("App", ["SDK"]), ("OTLP", ["the protocol"]), ("Collector", ["routes"]), ("Backend", ["swap without rewrite"])],
      "A app fala OTLP. Trocar Jaeger por Tempo é config do collector, não rewrite do código.",
      "The app speaks OTLP. Switching Jaeger for Tempo is collector config, not a code rewrite.",
      "d-otel"),
    C("Security Chaos Engineering", 0, "cycle", "Experimento, não vandalismo", "Experiment, not vandalism",
      ["Hipótese", "Explosão pequena", "Métrica", "Para"],
      ["Hypothesis", "Small blast", "Metric", "Stop"],
      "Tem hipótese, tamanho limitado e um jeito de parar. Sem isso é incidente, não experimento.",
      "It has a hypothesis, a limited size, and a way to stop. Without that it is an incident, not an experiment.",
      "d-chaos"),
    C("Security Chaos Engineering", 2, "cols", "O que se prova", "What you prove",
      [("Disponibilidade", ["cai bem?"]), ("Detecção", ["viu?"]), ("Resposta", ["conteve?"])],
      [("Availability", ["fails well?"]), ("Detection", ["did it see?"]), ("Response", ["did it contain?"])],
      "Três perguntas diferentes. Um teste de queda não prova que o alerta existe.",
      "Three different questions. A failure test does not prove the alert exists.",
      "d-chaos-kinds"),
    C("Incident Response", 0, "cycle", "Ciclo, não lista", "A cycle, not a list",
      ["Detectar", "Conter", "Erradicar", "Recuperar"],
      ["Detect", "Contain", "Eradicate", "Recover"],
      "Acabar a lista não acaba o incidente. O ciclo volta na detecção seguinte.",
      "Finishing the list does not finish the incident. The cycle returns at the next detection.",
      "d-nist"),
    C("Incident Response", 2, "cols", "Severidade antes", "Severity beforehand",
      [("SEV1", ["acorda"]), ("SEV2", ["horário"]), ("SEV3", ["fila"])],
      [("SEV1", ["wakes people"]), ("SEV2", ["business hours"]), ("SEV3", ["queue"])],
      "A definição existe antes das três da manhã. Na hora, só se consulta.",
      "The definition exists before 3 a.m. At the time, you only look it up.",
      "d-sev"),
    C("Compliance Contínuo", 0, "cols", "Qual framework", "Which framework",
      [("Negócio", ["o que você faz"]), ("Framework", ["SOC 2", "ISO"]), ("Controle", ["o que provar"])],
      [("Business", ["what you do"]), ("Framework", ["SOC 2", "ISO"]), ("Control", ["what to prove"])],
      "Framework não é troféu. É o conjunto de controles que o seu caso exige.",
      "A framework is not a trophy. It is the set of controls your case requires.",
      "d-frameworks"),
    C("Compliance Contínuo", 2, "cols", "Base legal", "Legal basis",
      [("Dado", ["pessoal"]), ("Base", ["documentada"]), ("Tratamento", ["só com ela"])],
      [("Data", ["personal"]), ("Basis", ["documented"]), ("Processing", ["only with it"])],
      "Tratar dado pessoal sem a base escrita é o controle que falta, mesmo com o resto verde.",
      "Processing personal data without the written basis is the missing control, even if the rest is green.",
      "d-legal"),
    C("Fundamentos de Python moderno", 0, "fanout", "Tudo é objeto", "Everything is an object",
      "objeto", ["int", "str", "função", "módulo"],
      "object", ["int", "str", "function", "module"],
      "Não há tipo 'primitivo' escondido. Número, texto, função e módulo são objetos.",
      "There is no hidden 'primitive' type. Number, text, function, and module are objects.",
      "d-py-objects"),
    C("Fundamentos de Python moderno", 2, "cols", "for", "for",
      [("Iterável", ["a fonte"]), ("Iterador", ["o próximo"]), ("Corpo", ["um item"])],
      [("Iterable", ["the source"]), ("Iterator", ["the next"]), ("Body", ["one item"])],
      "O for pede o próximo item. Ele não conta índice, a menos que você peça enumerate.",
      "for asks for the next item. It does not count an index unless you ask for enumerate.",
      "d-py-for"),
    C("Estruturas de dados e código Pythonic", 0, "cols", "Qual recipiente", "Which container",
      [("list", ["ordem"]), ("set", ["único"]), ("dict", ["chave"])],
      [("list", ["order"]), ("set", ["unique"]), ("dict", ["key"])],
      "A escolha muda o custo de buscar. Lista percorre; set e dict apontam.",
      "The choice changes the cost of lookup. A list scans; a set and a dict point.",
      "d-py-data"),
    C("Estruturas de dados e código Pythonic", 2, "cols", "Generator", "Generator",
      [("Fonte", ["grande"]), ("yield", ["um item"]), ("Consumidor", ["não vê a lista"])],
      [("Source", ["large"]), ("yield", ["one item"]), ("Consumer", ["never sees the list"])],
      "O generator não monta a lista. Entrega um item e espera o próximo pedido.",
      "The generator does not build the list. It hands over one item and waits for the next request.",
      "d-py-gen"),
    C("POO, exceções e context managers", 0, "cols", "__new__ e __init__", "__new__ and __init__",
      [("__new__", ["constrói"]), ("objeto", ["já existe"]), ("__init__", ["mobília"])],
      [("__new__", ["constructs"]), ("object", ["already exists"]), ("__init__", ["furnishes"])],
      "Quando __init__ roda, o objeto já foi criado. Ele só preenche o que já existe.",
      "When __init__ runs, the object has already been created. It only fills what already exists.",
      "d-py-init"),
    C("POO, exceções e context managers", 2, "cols", "super()", "super()",
      [("Filha", ["o específico"]), ("super()", ["sobe"]), ("Pai", ["o comum"])],
      [("Child", ["the specific"]), ("super()", ["goes up"]), ("Parent", ["the shared"])],
      "super() chama o próximo da cadeia. A filha não copia o método do pai.",
      "super() calls the next in the chain. The child does not copy the parent's method.",
      "d-py-super"),
    C("Manipulação de arquivos, paths e CLI", 0, "cols", "pathlib", "pathlib",
      [("String", ["texto solto"]), ("Path", ["sabe que é caminho"]), ("open", ["o arquivo"])],
      [("String", ["loose text"]), ("Path", ["knows it is a path"]), ("open", ["the file"])],
      "Path junta e normaliza caminho. A string não sabe a diferença entre pasta e texto.",
      "Path joins and normalizes a path. A string does not know the difference between a folder and text.",
      "d-py-path"),
    C("Manipulação de arquivos, paths e CLI", 2, "cols", "YAML seguro", "Safe YAML",
      [("Arquivo", ["texto"]), ("safe_load", ["dados"]), ("load", ["pode executar"])],
      [("File", ["text"]), ("safe_load", ["data"]), ("load", ["can execute"])],
      "safe_load só devolve dados. O load antigo pode construir objeto e rodar código.",
      "safe_load only returns data. The old load can build an object and run code.",
      "d-py-yaml"),
    C("HTTP, APIs REST e SDKs", 0, "cols", "requests", "requests",
      [("Chamada", ["URL"]), ("timeout", ["não espera para sempre"]), ("raise_for_status", ["HTTP ruim vira erro"])],
      [("Call", ["URL"]), ("timeout", ["does not wait forever"]), ("raise_for_status", ["bad HTTP becomes an error"])],
      "Sem timeout a chamada pode pendurar. Sem raise_for_status, o 500 parece sucesso.",
      "Without a timeout the call can hang. Without raise_for_status, a 500 looks like success.",
      "d-py-http"),
    C("HTTP, APIs REST e SDKs", 2, "cycle", "Retry", "Retry",
      ["Pedido", "Falhou?", "Backoff", "De novo"],
      ["Request", "Failed?", "Backoff", "Again"],
      "Só repete falha transitória. Erro de lógica repetido só multiplica o estrago.",
      "Only retry a transient failure. A repeated logic error only multiplies the damage.",
      "d-py-retry"),
    C("Automação de sistema com Python", 0, "cols", "subprocess", "subprocess",
      [("Lista", ["arg1", "arg2"]), ("sem shell", ["não reinterpreta"]), ("Processo", ["roda"])],
      [("List", ["arg1", "arg2"]), ("no shell", ["does not reinterpret"]), ("Process", ["runs"])],
      "Cada argumento é um item da lista. Uma string única passa pelo shell e pode ser reescrita.",
      "Each argument is one list item. A single string goes through the shell and can be rewritten.",
      "d-py-subprocess"),
    C("Automação de sistema com Python", 2, "cols", "Ambiente do processo", "Process environment",
      [("Pai", ["env herdado"]), ("override", ["só o que muda"]), ("Filho", ["o resto igual"])],
      [("Parent", ["inherited env"]), ("override", ["only what changes"]), ("Child", ["the rest the same"])],
      "O filho herda o ambiente. Passe só a chave que precisa mudar, não um ambiente vazio sem querer.",
      "The child inherits the environment. Pass only the key that must change, not an empty environment by accident.",
      "d-py-env"),
    C("Concorrência: threads, asyncio e multiprocessing", 0, "fanout", "O GIL", "The GIL",
      "Um bytecode", ["Thread A", "Thread B", "Thread C"],
      "One bytecode", ["Thread A", "Thread B", "Thread C"],
      "Várias threads esperam. O cadeado deixa uma só executar bytecode Python por vez.",
      "Several threads wait. The lock lets only one execute Python bytecode at a time.",
      "d-py-gil"),
    C("Concorrência: threads, asyncio e multiprocessing", 2, "cycle", "asyncio", "asyncio",
      ["Task A espera I/O", "Loop", "Task B roda", "Volta"],
      ["Task A waits on I/O", "Loop", "Task B runs", "Back"],
      "Uma thread só. Enquanto uma task espera a rede, outra usa o processador.",
      "One thread only. While one task waits on the network, another uses the processor.",
      "d-py-async"),
    C("Testes com pytest, mocks e cobertura", 0, "cols", "pytest", "pytest",
      [("teste", ["função"]), ("assert", ["a condição"]), ("falha", ["mostra o valor"])],
      [("test", ["function"]), ("assert", ["the condition"]), ("failure", ["shows the value"])],
      "O teste é função e assert. A falha mostra os dois lados, sem self.assertEqual.",
      "The test is a function and assert. The failure shows both sides, without self.assertEqual.",
      "d-py-pytest"),
    C("Testes com pytest, mocks e cobertura", 2, "cols", "Fixture", "Fixture",
      [("fixture", ["prepara"]), ("teste", ["recebe"]), ("teardown", ["desfaz"])],
      [("fixture", ["prepares"]), ("test", ["receives"]), ("teardown", ["undoes"])],
      "A fixture injeta a dependência e desfaz depois. O teste não monta o mundo na mão.",
      "The fixture injects the dependency and undoes it after. The test does not build the world by hand.",
      "d-py-fixture"),
    C("Empacotamento moderno e qualidade de código", 0, "cols", "Ambiente virtual", "Virtual environment",
      [("Projeto A", ["venv A"]), ("Python", ["o do sistema"]), ("Projeto B", ["venv B"])],
      [("Project A", ["venv A"]), ("Python", ["the system one"]), ("Project B", ["venv B"])],
      "Cada projeto tem o próprio vaso de dependências. O do sistema fica de fora.",
      "Each project has its own dependency pot. The system one stays out.",
      "d-py-venv"),
    C("Empacotamento moderno e qualidade de código", 2, "fanout", "pyproject.toml", "pyproject.toml",
      "pyproject.toml", ["build", "deps", "ruff"],
      "pyproject.toml", ["build", "deps", "ruff"],
      "Um arquivo declara build, dependência e ferramenta. Três arquivos soltos divergem.",
      "One file declares build, dependency, and tooling. Three loose files drift apart.",
      "d-py-pyproject"),
    C("Python para DevSecOps na prática", 0, "cols", "boto3 sem chave no código", "boto3 with no key in code",
      [("Código", ["sem segredo"]), ("Role", ["a identidade"]), ("AWS", ["a API"])],
      [("Code", ["no secret"]), ("Role", ["the identity"]), ("AWS", ["the API"])],
      "A credencial fica na role da máquina ou do cofre. O fonte não carrega access key.",
      "The credential stays on the machine role or in the vault. The source carries no access key.",
      "d-py-boto"),
    C("Python para DevSecOps na prática", 2, "cycle", "Watch, não poll cego", "Watch, not blind poll",
      ["API", "Evento", "Handler", "Espera"],
      ["API", "Event", "Handler", "Wait"],
      "O watch entrega a mudança. Perguntar em loop gasta cota e chega atrasado.",
      "The watch delivers the change. Asking in a loop spends quota and arrives late.",
      "d-py-watch"),
]


def main() -> None:
    LESSONS.mkdir(parents=True, exist_ok=True)
    # fotos de objeto da rodada anterior
    for old in LESSONS.glob("c-*.jpg"):
        old.unlink()

    by_topic: dict[str, list[dict]] = {}
    for spec in SPECS:
        by_topic.setdefault(spec["topic"], []).append(spec)
        for lang, suffix in (("pt", ""), ("en", "-en")):
            frames = render(spec["kind"], spec["title"][lang], spec["payload"][lang], lang)
            save_gif(frames, LESSONS / f"{spec['file']}{suffix}.gif")

    photo = re.compile(
        r'\n?<figure class="lesson-figure">\s*<img src="/static/img/lessons/[^"]+"[^>]*>\s*<figcaption>.*?</figcaption>\s*</figure>',
        re.S,
    )
    for path in sorted(SEED.glob("phase*.py")):
        text = path.read_text()
        text = photo.sub("", text)
        marks = [m.start() for m in re.finditer(r"\n        \{\n", text)]
        # aplica de trás para frente para os offsets anteriores permanecerem
        chunks = []
        cursor = 0
        spans = []
        for i, start in enumerate(marks):
            end = marks[i + 1] if i + 1 < len(marks) else len(text)
            spans.append((start, end))
        for start, end in reversed(spans):
            chunk = text[start:end]
            title_m = re.search(r'"title": "([^"]+)"', chunk)
            if not title_m or title_m.group(1) not in by_topic:
                continue
            en_at = chunk.find('"body_en"')
            if en_at < 0:
                raise SystemExit(f"sem body_en: {title_m.group(1)}")
            pt, en = chunk[:en_at], chunk[en_at:]
            pt_h3 = re.findall(r"<h3>(.*?)</h3>", pt)
            en_h3 = re.findall(r"<h3>(.*?)</h3>", en)
            if len(pt_h3) != len(en_h3):
                raise SystemExit(f"h3 PT/EN diferem em {title_m.group(1)}: {len(pt_h3)} vs {len(en_h3)}")
            # seções maiores primeiro
            for spec in sorted(by_topic[title_m.group(1)], key=lambda s: -s["section"]):
                sec = spec["section"]
                if sec >= len(pt_h3):
                    raise SystemExit(f"seção {sec} inexistente em {title_m.group(1)}")
                pt = insert_after(
                    pt,
                    pt_h3[sec],
                    figure(f"{spec['file']}.gif", spec["alt"]["pt"], spec["cap"]["pt"]),
                )
                en = insert_after(
                    en,
                    en_h3[sec],
                    figure(f"{spec['file']}-en.gif", spec["alt"]["en"], spec["cap"]["en"]),
                )
            text = text[:start] + pt + en + text[end:]
        path.write_text(text)
        print(path.name, "ok")

    gifs = list(LESSONS.glob("d-*.gif"))
    print("gifs", len(gifs), "bytes", sum(p.stat().st_size for p in gifs))


if __name__ == "__main__":
    main()
