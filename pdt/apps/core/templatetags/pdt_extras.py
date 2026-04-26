"""Filtros de template customizados do PDT."""
from __future__ import annotations

import re

from django import template
from django.utils.html import escape, linebreaks
from django.utils.safestring import mark_safe

register = template.Library()

# Separadores comuns nas alternativas do simulador (trecho inicial = “resposta”, resto = contexto).
_INTERVIEW_CHOICE_SPLITTERS = ("; ", ", mas ", ", porém ")

# Padrão "sujeito-comando" no início da opção: um ou mais termos em crase
# (com sigla/aposto curto entre parênteses opcional), ligados por "e"/"ou"/"/"/",".
# Quando bate, o restante é a descrição do que o sujeito faz e não deve aparecer na prova.
_SUBJECT_TOKEN = r"`[^`\n]+`(?:\s*\([^)\n]{1,40}\))?"
_SUBJECT_LEAD_RE = re.compile(
    rf"^\s*(?P<subject>{_SUBJECT_TOKEN}(?:\s*(?:e|ou|/|,)\s*{_SUBJECT_TOKEN})*)"
)


@register.filter
def interview_choice_lead(text) -> str:
    """Texto mostrado na prova: só o núcleo da alternativa, sem explicação que facilite demais.

    No gabarito use o texto integral (`bold_ticks` na alternativa completa).
    """
    text = (text or "").strip()
    if not text:
        return ""

    # 1) Opção começa com sujeito-comando em crase: mostra só o(s) termo(s).
    m = _SUBJECT_LEAD_RE.match(text)
    if m:
        subject = m.group("subject").strip().rstrip(",")
        rest = text[m.end():].lstrip()
        if rest:
            return subject
        # Sem cauda → a opção já é só o sujeito; devolve original.
        return text

    # 2) Conectores explícitos: trecho inicial é a "resposta", o resto é contexto.
    for sep in _INTERVIEW_CHOICE_SPLITTERS:
        idx = _find_outside_parens(text, sep)
        if idx >= 0:
            return text[:idx].strip().rstrip(",")

    # 3) Frase única longa (comum em sênior): corta na primeira «, » fora de parênteses.
    if len(text) > 120:
        idx = _find_outside_parens(text, ", ")
        if idx >= 22:
            return text[:idx].strip().rstrip(",")
    return text


def _find_outside_parens(text: str, needle: str) -> int:
    """Posição da primeira ocorrência de `needle` fora de parênteses, ou -1.

    Evita cortar dentro de listas como «(Okta, Auth0)», o que deixaria parênteses
    abertos no texto exibido na prova.
    """
    depth = 0
    n = len(needle)
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        elif depth == 0 and text.startswith(needle, i):
            return i
    return -1


@register.filter
def interview_choice_detail(text) -> str:
    """Trecho explicativo da alternativa, se existir (após `; ` ou «, mas » / «, porém »)."""
    text = (text or "").strip()
    if not text:
        return ""
    for sep in _INTERVIEW_CHOICE_SPLITTERS:
        if sep in text:
            tail = text.split(sep, 1)[1].strip()
            if sep == ", mas ":
                return "mas " + tail
            if sep == ", porém ":
                return "porém " + tail
            return tail
    return ""


@register.filter
def nav_section_active(request, section: str) -> bool:
    """Indica se a rota atual pertence à seção principal do menu (Dashboard, Trilha, …).

    Uso: {% if request|nav_section_active:'dashboard' %}
    """
    if not request:
        return False
    rm = getattr(request, "resolver_match", None)
    if not rm:
        return False
    ns = rm.namespace or ""
    name = rm.url_name or ""
    if section == "dashboard":
        return ns == "core" and name == "dashboard"
    if section == "courses":
        return ns == "courses"
    if section == "radar":
        return ns == "gamification" and name == "radar"
    if section == "leaderboard":
        return ns == "gamification" and name == "leaderboard"
    if section == "presence":
        return ns == "presence"
    if section == "interviews":
        return ns == "interviews"
    return False


@register.filter(needs_autoescape=True)
def bold_ticks(value, autoescape=True):
    """Troca trechos `assim` por <strong>assim</strong> (sem crases), para leitura mais limpa."""
    if value is None:
        return ""
    text = str(value)
    if autoescape:
        text = escape(text)
    out = re.sub(r"`([^`]+)`", r"<strong>\1</strong>", text)
    return mark_safe(out)


@register.filter(is_safe=True)
def render_lesson(value: str) -> str:
    """Renderiza campo de aula.

    - Se o conteúdo já contém HTML (começa com '<'), retorna como safe diretamente.
    - Caso contrário, aplica `linebreaks` (texto puro → <p>) e retorna safe.
    """
    if not value:
        return ""
    stripped = value.strip()
    if stripped.startswith("<"):
        return mark_safe(stripped)
    return mark_safe(linebreaks(stripped))


@register.filter
def get_item(dictionary, key):
    """Retorna dictionary[key], ou None se não existir.

    Uso no template: {{ scores|get_item:topic.id }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def points_of(score_obj) -> int:
    """Retorna o número de pontos de um objeto TopicScore (ou 0 se None).

    Uso no template: {{ score|points_of }}
    """
    if score_obj is None:
        return 0
    return getattr(score_obj, "points", 0)
