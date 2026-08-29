"""Expande o catálogo de 60 labs autorais para 1 lab por página de aula.

O lab escrito à mão em `labs.py` (1 por tópico) cai na página cujo texto
mais combina com o cenário; as demais páginas ganham um exercício gerado
a partir do próprio HTML — comando da seção (terminal) ou pergunta de
foco (scenario).
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
_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")

_DISTRACTORS = (
    "sudo",
    "grep",
    "cat",
    "echo",
    "--help",
    "-v",
    "head",
    "tail",
    "chmod",
    "777",
)

_GENERIC_WRONG_PT = (
    "Isso pode ser ignorado se o serviço já está no ar.",
    "A prática recomendada é `chmod 777` em produção.",
)
_GENERIC_WRONG_EN = (
    "This can be ignored if the service is already up.",
    "The recommended practice is `chmod 777` in production.",
)


def _plain(html: str) -> str:
    text = _TAG_RE.sub("", html)
    return html_lib.unescape(re.sub(r"\s+", " ", text)).strip()


def _page_headings(page_html: str) -> list[str]:
    return [_plain(m) for m in _H3_RE.findall(page_html) if _plain(m)]


def _first_command_tokens(page_html: str) -> list[str] | None:
    for block in _CODE_BLOCK_RE.findall(page_html):
        text = html_lib.unescape(_TAG_RE.sub("", block))
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith("$"):
                line = line[1:].strip()
            if not line or line.startswith("#"):
                continue
            line = re.split(r"\s+#", line, 1)[0].strip()
            if not line:
                continue
            try:
                toks = shlex.split(line, posix=True)
            except ValueError:
                toks = line.split()
            toks = [t for t in toks if t]
            if 2 <= len(toks) <= 7:
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
    """Aceita `cmd +flag arg` e `cmd arg +flag` quando o último token é flag."""
    if len(tokens) >= 3 and tokens[-1].startswith(("+", "-")):
        swapped = [tokens[0], tokens[-1], *tokens[1:-1]]
        if swapped != tokens:
            return [swapped]
    if len(tokens) >= 3 and tokens[1].startswith(("+", "-")):
        # cmd +flag rest → cmd rest +flag
        swapped = [tokens[0], *tokens[2:], tokens[1]]
        if swapped != tokens:
            return [swapped]
    return []


def _short_title(headings: list[str], page: int) -> tuple[str, str]:
    raw = headings[0] if headings else f"Página {page}"
    raw = re.sub(r"^\d+\.\s*", "", raw)
    if len(raw) > 48:
        raw = raw[:45].rstrip() + "…"
    return f"Pratique: {raw}", f"Practice: {raw}"


def _synthesize_terminal(
    tokens: list[str], headings: list[str], page: int
) -> dict[str, Any]:
    title, title_en = _short_title(headings, page)
    tema = headings[0] if headings else f"página {page}"
    cmd = " ".join(tokens)
    alts = _flag_swap(tokens)
    spec = {
        "scenario": (
            f"Com base nesta página ({tema}), monte o comando visto na aula."
        ),
        "correct_command": tokens,
        "distractor_tokens": _distractors_for(tokens),
        "explanation": f"O comando desta seção é `{cmd}`.",
    }
    spec_en = {
        "scenario": (
            f"Based on this page ({tema}), build the command shown in the lesson."
        ),
        "correct_command": tokens,
        "distractor_tokens": spec["distractor_tokens"],
        "explanation": f"The command in this section is `{cmd}`.",
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


def _synthesize_scenario(
    headings: list[str],
    other_headings: list[str],
    page: int,
) -> dict[str, Any]:
    title, title_en = _short_title(headings, page)
    correct = headings[0] if headings else f"Página {page}"
    wrongs = []
    for h in other_headings:
        if h != correct and h not in wrongs:
            wrongs.append(h)
        if len(wrongs) >= 2:
            break
    while len(wrongs) < 2:
        fallback = (
            _GENERIC_WRONG_PT[len(wrongs)]
            if len(wrongs) < len(_GENERIC_WRONG_PT)
            else f"Outro tema {len(wrongs)}"
        )
        wrongs.append(fallback)
    wrongs_en = []
    for i, w in enumerate(wrongs):
        if w in headings or w == correct:
            wrongs_en.append(w)
        else:
            wrongs_en.append(
                _GENERIC_WRONG_EN[i] if i < len(_GENERIC_WRONG_EN) else w
            )
    spec = {
        "situation": "Você acabou de ler esta página. Qual é o tema central dela?",
        "choices": [
            {
                "text": correct,
                "outcome": "Isso mesmo: é o foco desta página.",
                "good": True,
            },
            {
                "text": wrongs[0],
                "outcome": "Esse tema aparece em outra parte da aula, não nesta página.",
                "good": False,
            },
            {
                "text": wrongs[1],
                "outcome": "Esse tema aparece em outra parte da aula, não nesta página.",
                "good": False,
            },
        ],
        "explanation": f"Nesta página o fio condutor é: {correct}.",
    }
    spec_en = {
        "situation": "You just read this page. What is its central topic?",
        "choices": [
            {
                "text": correct,
                "outcome": "That's right: that is this page's focus.",
                "good": True,
            },
            {
                "text": wrongs_en[0],
                "outcome": "That topic appears elsewhere in the lesson, not on this page.",
                "good": False,
            },
            {
                "text": wrongs_en[1],
                "outcome": "That topic appears elsewhere in the lesson, not on this page.",
                "good": False,
            },
        ],
        "explanation": f"The through-line on this page is: {correct}.",
    }
    return {
        "kind": "scenario",
        "title": title,
        "title_en": title_en,
        "spec": spec,
        "spec_en": spec_en,
    }


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
    words = {w for w in re.findall(r"[a-z0-9_+./:-]{4,}", blob) if w not in {"você", "this", "that", "para", "com"}}
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
            pages, pages_en = _topic_pages(topic)
            all_headings = []
            for p in pages:
                all_headings.extend(_page_headings(p))
            authored = authored_by_title.get(topic["title"])
            authored_page = (
                assign_authored_page(pages, authored) if authored else None
            )
            for i, page in enumerate(pages, start=1):
                if authored and i == authored_page:
                    entry = {**authored, "lesson_page": i, "order": i}
                    out.append(entry)
                    continue
                headings = _page_headings(page)
                other = [h for h in all_headings if h not in headings]
                tokens = _first_command_tokens(page)
                if tokens:
                    built = _synthesize_terminal(tokens, headings, i)
                else:
                    built = _synthesize_scenario(headings, other, i)
                out.append(
                    {
                        "topic_title": topic["title"],
                        "lesson_page": i,
                        "order": i,
                        **built,
                    }
                )
    return out
