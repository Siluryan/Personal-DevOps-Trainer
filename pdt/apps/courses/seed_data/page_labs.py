"""Expande o catálogo de 60 labs autorais para 1 lab prático por página.

O lab escrito à mão em `labs.py` cai na página cujo texto mais combina com
o cenário. As demais páginas ganham um exercício gerado do HTML da própria
seção, nesta ordem de preferência:

  1. terminal — comando em `<pre><code>` ou `<code>` inline
  2. order    — checklist / etapas numeradas da página
  3. find_flaw — anti-pattern: a linha perigosa no meio de um snippet
  4. blanks   — preencher um path ou flag citado na aula
  5. scenario — decisão prática (nunca “qual o tema da página”)
"""
from __future__ import annotations

import html as html_lib
import re
import shlex
from typing import Any

from apps.core.pagination import paginate_html_sections

from . import PHASES
from .labs import LABS

_CODE_BLOCK_RE = re.compile(r"<pre><code>(.*?)</code></pre>", re.S)
_INLINE_CODE_RE = re.compile(r"<code>([^<]+)</code>")
_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
_STRONG_RE = re.compile(r"<strong>(.*?)</strong>", re.S)
_TR_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
_TD_RE = re.compile(r"<td>(.*?)</td>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")

_DISTRACTORS = (
    "sudo",
    "grep",
    "cat",
    "echo",
    "--help",
    "-v",
    "head",
    "chmod",
    "777",
    "rm",
    "-rf",
)

_SHELL_BINS = frozenset(
    {
        "ls",
        "cat",
        "find",
        "chmod",
        "chown",
        "dig",
        "ping",
        "ssh",
        "ssh-keygen",
        "ssh-keyscan",
        "curl",
        "wget",
        "systemctl",
        "journalctl",
        "kubectl",
        "docker",
        "git",
        "aws",
        "terraform",
        "ansible",
        "ansible-playbook",
        "iptables",
        "nft",
        "ufw",
        "ss",
        "ip",
        "uname",
        "id",
        "sudo",
        "setfacl",
        "getfacl",
        "nslookup",
        "traceroute",
        "tcpdump",
        "openssl",
        "helm",
        "cosign",
        "syft",
        "trivy",
        "apt",
        "apt-get",
        "dnf",
        "yum",
        "nmap",
        "nc",
        "netstat",
        "ps",
        "top",
        "df",
        "free",
        "mount",
        "useradd",
        "usermod",
        "passwd",
        "visudo",
        "setcap",
        "getcap",
        "strace",
        "lsof",
        "jq",
        "yq",
        "kubectl",
        "kube-linter",
        "hadolint",
        "checkov",
        "tfsec",
        "tflint",
        "pre-commit",
        "pytest",
        "ruff",
        "mypy",
        "bandit",
        "pip",
        "poetry",
        "uv",
        "python",
        "python3",
        "make",
        "systemctl",
        "sshd",
        "nginx",
        "set -euo",
        "set",
        "export",
        "source",
        "eval",
        "xargs",
        "awk",
        "sed",
        "tar",
        "rsync",
        "scp",
        "sftp",
        "vault",
        "consul",
        "nomad",
        "pack",
        "buildah",
        "podman",
        "skopeo",
        "crane",
        "grype",
        "cosign",
        "rekor",
        "falco",
        "opa",
        "conftest",
        "kyverno",
        "istioctl",
        "linkerd",
        "prometheus",
        "amtool",
        "logcli",
        "stern",
        "k9s",
        "helmfile",
        "kustomize",
        "argocd",
        "flux",
        "gh",
        "hub",
        "az",
        "gcloud",
        "doctl",
        "pulumi",
        "packer",
        "vagrant",
        "virsh",
        "qm",
        "ctr",
        "nerdctl",
        "crictl",
        "nsenter",
        "unshare",
        "capsh",
        "getent",
        "aa-status",
        "sestatus",
        "ausearch",
        "auditctl",
    }
)

_ANTI_HINTS = (
    "anti-pattern",
    "antipattern",
    "anti-patterns",
    "não faça",
    "nunca ",
    "never ",
    "clássicos",
    "recorrentes",
    "o que pode dar errado",
)

def _plain(html: str) -> str:
    text = _TAG_RE.sub("", html)
    return html_lib.unescape(re.sub(r"\s+", " ", text)).strip()


def _page_headings(page_html: str) -> list[str]:
    return [_plain(m) for m in _H3_RE.findall(page_html) if _plain(m)]


def _page_text(page_html: str) -> str:
    return _plain(page_html)


def _tokenize(line: str) -> list[str] | None:
    line = line.strip()
    if line.startswith("$"):
        line = line[1:].strip()
    if not line or line.startswith("#"):
        return None
    line = re.split(r"\s+#", line, 1)[0].strip()
    if not line:
        return None
    try:
        toks = shlex.split(line, posix=True)
    except ValueError:
        toks = line.split()
    toks = [t for t in toks if t]
    if len(toks) > 8:
        toks = toks[:6]
    if 2 <= len(toks) <= 8:
        return toks
    return None


def _first_command_tokens(page_html: str) -> list[str] | None:
    for block in _CODE_BLOCK_RE.findall(page_html):
        text = html_lib.unescape(_TAG_RE.sub("", block))
        for raw in text.splitlines():
            toks = _tokenize(raw)
            if toks:
                return toks
    return None


def _inline_command_tokens(page_html: str) -> list[str] | None:
    for raw in _INLINE_CODE_RE.findall(page_html):
        text = html_lib.unescape(raw).strip()
        if not text or "\n" in text:
            continue
        first = text.split()[0]
        first = first.split("=")[0]
        if first not in _SHELL_BINS and not first.endswith("ctl"):
            continue
        toks = _tokenize(text)
        if toks:
            return toks
    return None


def _distractors_for(tokens: list[str], n: int = 3) -> list[str]:
    used = set(tokens)
    out: list[str] = []
    for d in _DISTRACTORS:
        if d not in used:
            out.append(d)
        if len(out) >= n:
            break
    return out


def _flag_swap(tokens: list[str]) -> list[list[str]]:
    if len(tokens) >= 3 and tokens[-1].startswith(("+", "-")):
        swapped = [tokens[0], tokens[-1], *tokens[1:-1]]
        if swapped != tokens:
            return [swapped]
    if len(tokens) >= 3 and tokens[1].startswith(("+", "-")):
        swapped = [tokens[0], *tokens[2:], tokens[1]]
        if swapped != tokens:
            return [swapped]
    return []


def _short_title(headings: list[str], page: int, prefix_pt: str, prefix_en: str) -> tuple[str, str]:
    raw = headings[0] if headings else f"Página {page}"
    raw = re.sub(r"^\d+\.\s*", "", raw)
    if len(raw) > 42:
        raw = raw[:39].rstrip() + "…"
    return f"{prefix_pt}: {raw}", f"{prefix_en}: {raw}"


def _synthesize_terminal(tokens: list[str], headings: list[str], page: int) -> dict[str, Any]:
    title, title_en = _short_title(headings, page, "Monte o comando", "Build the command")
    cmd = " ".join(tokens)
    alts = _flag_swap(tokens)
    spec = {
        "scenario": f"Monte o comando `{cmd}` desta página, só com as peças certas.",
        "correct_command": tokens,
        "distractor_tokens": _distractors_for(tokens),
        "explanation": f"`{cmd}` é o comando que a aula usa nesta seção.",
    }
    spec_en = {
        "scenario": f"Build the command `{cmd}` from this page, using only the right pieces.",
        "correct_command": tokens,
        "distractor_tokens": spec["distractor_tokens"],
        "explanation": f"`{cmd}` is the command this section uses.",
    }
    if alts:
        spec["accepted_commands"] = alts
        spec_en["accepted_commands"] = alts
    return {
        "kind": "terminal",
        "title": title,
        "title_en": title_en,
        "spec": spec,
        "spec_en": spec_en,
    }


def _checklist_steps(page_html: str) -> list[str]:
    steps: list[str] = []
    for raw in _LI_RE.findall(page_html):
        text = _plain(raw)
        if not text or len(text) > 140:
            continue
        text = re.sub(r"^\(\d+\)\s*", "", text)
        steps.append(text)
        if len(steps) >= 5:
            break
    return steps


def _synthesize_order(steps: list[str], headings: list[str], page: int) -> dict[str, Any]:
    title, title_en = _short_title(headings, page, "Ordene as etapas", "Order the steps")
    shuffled = list(reversed(steps))
    if shuffled == steps:
        shuffled = steps[1:] + steps[:1]
    return {
        "kind": "order",
        "title": title,
        "title_en": title_en,
        "spec": {
            "scenario": "Toque nas etapas na ordem em que você executaria na prática.",
            "steps_shuffled": shuffled,
            "correct_order": steps,
            "explanation": "A ordem segue o checklist desta página: do reconhecimento à ação.",
        },
        "spec_en": {
            "scenario": "Tap the steps in the order you would actually run them.",
            "steps_shuffled": shuffled,
            "correct_order": steps,
            "explanation": "The order follows this page's checklist: recon first, then action.",
        },
    }


def _is_anti_page(page_html: str, headings: list[str]) -> bool:
    blob = (_page_text(page_html) + " " + " ".join(headings)).lower()
    return any(h in blob for h in _ANTI_HINTS)


def _dangerous_inline(page_html: str) -> str | None:
    danger = (
        "777",
        "permitrootlogin yes",
        "stricthostkeychecking=no",
        "eval ",
        "rm -rf",
        "curl | sh",
        "curl|sh",
        "privileged: true",
        "hostnetwork: true",
        "0.0.0.0/0",
        "latest",
        "password=",
        "aws_secret",
    )
    for raw in _INLINE_CODE_RE.findall(page_html):
        text = html_lib.unescape(raw).strip()
        if any(d in text.lower() for d in danger):
            return text[:80]
    return None


def _synthesize_find_flaw(page_html: str, headings: list[str], page: int) -> dict[str, Any] | None:
    bad = _dangerous_inline(page_html)
    if not bad:
        return None
    title, title_en = _short_title(headings, page, "Ache a falha", "Find the flaw")
    lines = [
        "#!/bin/bash",
        "set -euo pipefail",
        bad,
        "echo ok",
        "exit 0",
    ]
    return {
        "kind": "find_flaw",
        "title": title,
        "title_en": title_en,
        "spec": {
            "scenario": "Este snippet mistura rotina saudável com o anti-pattern da página. Toque na linha perigosa.",
            "lines": lines,
            "flaw_line_index": 2,
            "explanation": f"`{bad}` é exatamente o anti-pattern que esta seção pede para evitar.",
        },
        "spec_en": {
            "scenario": "This snippet mixes healthy boilerplate with this page's anti-pattern. Tap the dangerous line.",
            "lines": lines,
            "flaw_line_index": 2,
            "explanation": f"`{bad}` is the anti-pattern this section tells you to avoid.",
        },
    }


def _extract_paths(page_html: str) -> list[str]:
    found: list[str] = []
    for raw in _INLINE_CODE_RE.findall(page_html):
        text = html_lib.unescape(raw).strip()
        if re.fullmatch(r"/[A-Za-z0-9._\-/]+", text) and len(text) < 40:
            if text not in found:
                found.append(text)
    return found[:6]


def _synthesize_blanks_path(paths: list[str], headings: list[str], page: int) -> dict[str, Any] | None:
    if len(paths) < 2:
        return None
    correct = paths[0]
    options = paths[:3]
    while len(options) < 3:
        for extra in ("/tmp", "/home", "/var/tmp", "/opt"):
            if extra not in options:
                options.append(extra)
                break
        else:
            break
    title, title_en = _short_title(headings, page, "Complete o path", "Fill in the path")
    return {
        "kind": "blanks",
        "title": title,
        "title_en": title_en,
        "spec": {
            "scenario": "Você precisa abrir o path que esta página usa na prática.",
            "template": "Abrir ___PATH___",
            "blanks": {"PATH": {"options": options, "correct": correct}},
            "explanation": f"Nesta página o path da operação é `{correct}`.",
        },
        "spec_en": {
            "scenario": "You need to open the path this page uses in practice.",
            "template": "Open ___PATH___",
            "blanks": {"PATH": {"options": options, "correct": correct}},
            "explanation": f"On this page the path for the operation is `{correct}`.",
        },
    }


def _strong_terms(page_html: str) -> list[str]:
    terms: list[str] = []
    for raw in _STRONG_RE.findall(page_html):
        text = _plain(raw)
        if 2 <= len(text) <= 40 and text not in terms:
            terms.append(text)
    return terms[:4]


def _table_rows(page_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in _TR_RE.findall(page_html):
        cells = [_plain(td) for td in _TD_RE.findall(tr)]
        cells = [c for c in cells if c]
        if len(cells) >= 2:
            rows.append(cells)
    return rows


_CONSTRAINT_RE = re.compile(
    r"não |nunca |exige|exigid|precisa|preciso|quando |garant|proibid|"
    r"somente |só |apenas |em vez|ao custo|útil|imposs|deve |não pode",
    re.I,
)


def _strong_clauses(page_html: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for match in _STRONG_RE.finditer(page_html):
        term = _plain(match.group(1))
        if not (2 <= len(term) <= 40):
            continue
        after = _plain(page_html[match.end() : match.end() + 500])
        after = re.sub(r"^[\s,;:—\-–()]+", "", after)
        clause = re.split(r"(?<=[.!?])\s", after, 1)[0].strip()
        clause = re.sub(r"\s+", " ", clause)
        if len(clause) > 180:
            clause = clause[:177].rsplit(" ", 1)[0] + "…"
        if len(clause) < 28:
            continue
        if ")" in clause[:40] and "(" not in clause[:40]:
            continue
        pairs.append((term, clause))
    return pairs


def _synthesize_strong_scenario(
    page_html: str, headings: list[str], page: int
) -> dict[str, Any] | None:
    pairs = _strong_clauses(page_html)
    if len(pairs) < 2:
        return None
    picked = next((p for p in pairs[1:] if _CONSTRAINT_RE.search(p[1])), None)
    if picked is None:
        picked = pairs[1]
    term, clause = picked
    wrongs = [name for name, _ in pairs if name != term][:2]
    while len(wrongs) < 2:
        extra = "chmod 777" if "chmod 777" not in wrongs else "0.0.0.0/0"
        wrongs.append(extra)
    title, title_en = _short_title(headings, page, "Escolha na prática", "Pick in practice")
    return {
        "kind": "scenario",
        "title": title,
        "title_en": title_en,
        "spec": {
            "situation": f"Requisito: {clause} Qual opção desta página atende?",
            "choices": [
                {
                    "text": term,
                    "outcome": "Certo: é o que a aula associa a esse requisito.",
                    "good": True,
                },
                {
                    "text": wrongs[0],
                    "outcome": "Esse termo é de outro caso desta página — não atende o requisito.",
                    "good": False,
                },
                {
                    "text": wrongs[1],
                    "outcome": "Não é a opção para esse requisito.",
                    "good": False,
                },
            ],
            "explanation": f"Para esse requisito a aula aponta `{term}`.",
        },
        "spec_en": {
            "situation": f"Requirement: {clause} Which option from this page meets it?",
            "choices": [
                {
                    "text": term,
                    "outcome": "Right: that is what the lesson maps to this requirement.",
                    "good": True,
                },
                {
                    "text": wrongs[0],
                    "outcome": "That term belongs to another case on this page — it does not meet the requirement.",
                    "good": False,
                },
                {
                    "text": wrongs[1],
                    "outcome": "That is not the option for this requirement.",
                    "good": False,
                },
            ],
            "explanation": f"For this requirement the lesson points to `{term}`.",
        },
    }


_MATRIX_ROW_LABELS = frozenset(
    {
        "você controla",
        "provedor controla",
        "exemplos",
        "esforço operacional",
        "lock-in",
        "granularidade",
        "computação",
        "identidade",
        "rede",
        "object storage",
        "sql gerenciado",
        "nosql",
        "serverless function",
        "container managed",
    }
)
_WHEN_RE = re.compile(
    r"^(apps |quando |se |para |desenvolvimento|baseline|tráfego )",
    re.I,
)


def _synthesize_table_decision(
    rows: list[list[str]], headings: list[str], page: int
) -> dict[str, Any] | None:
    if len(rows) < 2:
        return None
    first, last = rows[0], rows[-1]
    if first[0].lower() in _MATRIX_ROW_LABELS:
        return None
    subject, action = first[0], first[-1]
    wrong = last[-1]
    if _WHEN_RE.match(action) or len(action) > len(subject) + 12:
        subject, action = action, subject
        wrong = last[0]
    if not subject or not action or action == wrong:
        return None
    if len(subject) < 4 or len(action) < 4:
        return None
    if len(subject) > 56:
        subject = subject[:53].rstrip() + "…"
    title, title_en = _short_title(headings, page, "Escolha a estratégia", "Pick the strategy")
    return {
        "kind": "scenario",
        "title": title,
        "title_en": title_en,
        "spec": {
            "situation": f"Para `{subject}`, o que a tabela desta página manda aplicar?",
            "choices": [
                {
                    "text": f"Aplicar `{action}`.",
                    "outcome": "Certo: é a linha que a tabela associa a esse caso.",
                    "good": True,
                },
                {
                    "text": f"Aplicar `{wrong}`.",
                    "outcome": "Essa linha é de outro caso da tabela — custo e risco não batem.",
                    "good": False,
                },
                {
                    "text": "Ignorar a tabela e abrir 0.0.0.0 / chmod 777 'só para testar'.",
                    "outcome": "Isso não é estratégia desta página — é o atalho que vira incidente.",
                    "good": False,
                },
            ],
            "explanation": f"Na tabela desta página, `{subject}` combina com `{action}`.",
        },
        "spec_en": {
            "situation": f"For `{subject}`, what does this page's table tell you to apply?",
            "choices": [
                {
                    "text": f"Apply `{action}`.",
                    "outcome": "Right: that is the row the table maps to this case.",
                    "good": True,
                },
                {
                    "text": f"Apply `{wrong}`.",
                    "outcome": "That row belongs to a different case — cost and risk do not match.",
                    "good": False,
                },
                {
                    "text": "Ignore the table and open 0.0.0.0 / chmod 777 'just to test'.",
                    "outcome": "That is not this page's strategy — it is the shortcut that becomes an incident.",
                    "good": False,
                },
            ],
            "explanation": f"In this page's table, `{subject}` maps to `{action}`.",
        },
    }


def _synthesize_decision(page_html: str, headings: list[str], page: int) -> dict[str, Any]:
    """Decisão prática: o que fazer vs o atalho perigoso, com base no texto."""
    title, title_en = _short_title(headings, page, "Decida na prática", "Decide in practice")
    inline = [html_lib.unescape(x).strip() for x in _INLINE_CODE_RE.findall(page_html)]
    good = next((c for c in inline if c and "777" not in c and "yes" not in c.lower()), None)
    bad = next((c for c in inline if "777" in c or "yes" in c.lower() or "rm -rf" in c), None)
    tema = headings[0] if headings else f"página {page}"
    strongs = _strong_terms(page_html)
    if good and bad and good != bad:
        choices_pt = [
            {"text": f"Usar `{good}`", "outcome": "Certo: é o que a aula recomenda aqui.", "good": True},
            {"text": f"Usar `{bad}`", "outcome": "Esse é o atalho que a página pede para evitar.", "good": False},
            {"text": "Deixar como está e só monitorar depois.", "outcome": "Adiar a correção deixa o risco no lugar.", "good": False},
        ]
        choices_en = [
            {"text": f"Use `{good}`", "outcome": "Right: that is what the lesson recommends here.", "good": True},
            {"text": f"Use `{bad}`", "outcome": "That is the shortcut this page tells you to avoid.", "good": False},
            {"text": "Leave it as-is and only monitor later.", "outcome": "Delaying the fix leaves the risk in place.", "good": False},
        ]
        explain_pt = f"Nesta seção a prática correta é `{good}`, não `{bad}`."
        explain_en = f"In this section the right move is `{good}`, not `{bad}`."
        situation_pt = f"Você está no cenário desta página ({tema}). Qual comando/controle aplica?"
        situation_en = f"You are in this page's scenario ({tema}). Which command/control do you apply?"
    elif strongs:
        primary = strongs[0]
        other = strongs[1] if len(strongs) > 1 else "um atalho genérico"
        choices_pt = [
            {
                "text": f"Aplicar `{primary}` como a aula descreve, no caso concreto.",
                "outcome": "Certo: é o controle/conceito que esta seção pede para usar.",
                "good": True,
            },
            {
                "text": f"Trocar `{primary}` por `{other}` sem olhar o contexto.",
                "outcome": "A página distingue os dois — misturar os termos quebra a operação.",
                "good": False,
            },
            {
                "text": "Abrir 0.0.0.0 e chmod 777 'só para testar' e lembrar de reverter depois.",
                "outcome": "Esse atalho vira permanente e é o anti-pattern mais comum.",
                "good": False,
            },
        ]
        choices_en = [
            {
                "text": f"Apply `{primary}` as the lesson describes, on the concrete case.",
                "outcome": "Right: that is the control/concept this section asks you to use.",
                "good": True,
            },
            {
                "text": f"Swap `{primary}` for `{other}` without checking context.",
                "outcome": "The page distinguishes the two — mixing the terms breaks the operation.",
                "good": False,
            },
            {
                "text": "Open 0.0.0.0 and chmod 777 'just to test' and remember to revert later.",
                "outcome": "That shortcut becomes permanent and is the most common anti-pattern.",
                "good": False,
            },
        ]
        explain_pt = f"O exercício pede para aplicar `{primary}` ({tema})."
        explain_en = f"The exercise asks you to apply `{primary}` ({tema})."
        situation_pt = f"Incidente no tema `{tema}`. Qual ação desta página você executa agora?"
        situation_en = f"Incident on `{tema}`. Which action from this page do you run now?"
    else:
        choices_pt = [
            {
                "text": f"Seguir o procedimento de `{tema}` com o menor privilégio possível.",
                "outcome": "Certo: a página ensina o controle concreto, não um atalho genérico.",
                "good": True,
            },
            {
                "text": "Abrir 0.0.0.0 e chmod 777 'só para testar' e lembrar de reverter depois.",
                "outcome": "Esse atalho vira permanente e é o anti-pattern mais comum.",
                "good": False,
            },
            {
                "text": "Ignorar o detalhe e só olhar o dashboard se alguém reclamar.",
                "outcome": "Sem o controle desta página o incidente chega antes do dashboard.",
                "good": False,
            },
        ]
        choices_en = [
            {
                "text": f"Follow the `{tema}` procedure with least privilege.",
                "outcome": "Right: the page teaches the concrete control, not a generic shortcut.",
                "good": True,
            },
            {
                "text": "Open 0.0.0.0 and chmod 777 'just to test' and remember to revert later.",
                "outcome": "That shortcut becomes permanent and is the most common anti-pattern.",
                "good": False,
            },
            {
                "text": "Ignore the detail and only check the dashboard if someone complains.",
                "outcome": "Without this page's control the incident arrives before the dashboard.",
                "good": False,
            },
        ]
        explain_pt = f"O exercício pede a ação desta página ({tema}), não o atalho perigoso."
        explain_en = f"The exercise asks for this page's action ({tema}), not the dangerous shortcut."
        situation_pt = f"Você está no cenário desta página ({tema}). O que faz agora?"
        situation_en = f"You are in this page's scenario ({tema}). What do you do now?"
    return {
        "kind": "scenario",
        "title": title,
        "title_en": title_en,
        "spec": {
            "situation": situation_pt,
            "choices": choices_pt,
            "explanation": explain_pt,
        },
        "spec_en": {
            "situation": situation_en,
            "choices": choices_en,
            "explanation": explain_en,
        },
    }


def _tokens_are_antipattern(tokens: list[str]) -> bool:
    joined = " ".join(tokens).lower()
    return any(
        needle in joined
        for needle in (
            "777",
            "rm -rf",
            "eval ",
            "permitrootlogin yes",
            "stricthostkeychecking=no",
            "curl | sh",
        )
    )


def synthesize_page_lab(page_html: str, headings: list[str], page: int) -> dict[str, Any]:
    tokens = _first_command_tokens(page_html) or _inline_command_tokens(page_html)
    if tokens and not _tokens_are_antipattern(tokens):
        return _synthesize_terminal(tokens, headings, page)
    if tokens and _tokens_are_antipattern(tokens):
        flaw = _synthesize_find_flaw(page_html, headings, page)
        if flaw:
            return flaw

    steps = _checklist_steps(page_html)
    if len(steps) >= 3:
        return _synthesize_order(steps, headings, page)

    if _is_anti_page(page_html, headings):
        flaw = _synthesize_find_flaw(page_html, headings, page)
        if flaw:
            return flaw

    paths = _extract_paths(page_html)
    blanks = _synthesize_blanks_path(paths, headings, page)
    if blanks:
        return blanks

    table = _synthesize_table_decision(_table_rows(page_html), headings, page)
    if table:
        return table

    strong = _synthesize_strong_scenario(page_html, headings, page)
    if strong:
        return strong

    return _synthesize_decision(page_html, headings, page)


def _score_page(page_html: str, authored: dict) -> int:
    blob = (
        authored.get("title", "")
        + " "
        + authored.get("title_en", "")
        + " "
        + (authored.get("spec") or {}).get("scenario", "")
        + " "
        + (authored.get("spec") or {}).get("explanation", "")
        + " "
        + " ".join((authored.get("spec") or {}).get("correct_command") or [])
    ).lower()
    words = {
        w
        for w in re.findall(r"[a-z0-9_+./:-]{4,}", blob)
        if w not in {"você", "this", "that", "para", "com"}
    }
    page_l = page_html.lower()
    return sum(1 for w in words if w in page_l)


def assign_authored_page(pages: list[str], authored: dict) -> int:
    if not pages:
        return 1
    best_i, best_s = 1, -1
    for i, page in enumerate(pages, start=1):
        s = _score_page(page, authored)
        if s > best_s:
            best_i, best_s = i, s
    return best_i


def _topic_pages(topic: dict) -> tuple[list[str], list[str]]:
    lesson = topic.get("lesson") or {}
    body = lesson.get("body") or ""
    body_en = lesson.get("body_en") or ""
    pages = paginate_html_sections(body) or ([body] if body else [""])
    pages_en = paginate_html_sections(body_en) if body_en else pages
    if len(pages_en) != len(pages):
        pages_en = pages
    return pages, pages_en


def expand_labs() -> list[dict[str, Any]]:
    """Lista pronta para o seed: 1 lab por (tópico, página)."""
    authored_by_title = {lab["topic_title"]: lab for lab in LABS}
    out: list[dict[str, Any]] = []
    for phase in PHASES:
        for topic in phase["topics"]:
            pages, _pages_en = _topic_pages(topic)
            authored = authored_by_title.get(topic["title"])
            authored_page = assign_authored_page(pages, authored) if authored else None
            for i, page in enumerate(pages, start=1):
                if authored and i == authored_page:
                    out.append({**authored, "lesson_page": i, "order": i})
                    continue
                headings = _page_headings(page)
                built = synthesize_page_lab(page, headings, i)
                out.append(
                    {
                        "topic_title": topic["title"],
                        "lesson_page": i,
                        "order": i,
                        **built,
                    }
                )
    return out
