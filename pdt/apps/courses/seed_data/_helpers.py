"""Helpers para construir entradas de questão de forma compacta."""
from __future__ import annotations

from apps.core.seed_utils import shuffle_seeded


def q(
    statement: str,
    correct: str,
    wrong: list[str],
    explanation: str = "",
    statement_en: str = "",
    correct_en: str = "",
    wrong_en: list[str] | None = None,
    explanation_en: str = "",
) -> dict:
    """Cria uma questão de múltipla escolha (1 correta + N erradas).

    As alternativas são embaralhadas para que a correta não esteja sempre na
    primeira posição. O embaralhamento é determinístico por enunciado.

    Os parâmetros `*_en` são opcionais: cada alternativa carrega seu par
    {text, text_en} no MESMO dict, então o embaralhamento desloca os dois
    juntos e a tradução nunca fica associada à alternativa errada.
    """
    wrong_en = wrong_en or []
    choices = [{"text": correct, "text_en": correct_en, "correct": True}]
    for i, w in enumerate(wrong):
        choices.append(
            {"text": w, "text_en": (wrong_en[i] if i < len(wrong_en) else ""), "correct": False}
        )
    shuffle_seeded(choices, statement)
    return {
        "statement": statement,
        "statement_en": statement_en,
        "explanation": explanation,
        "explanation_en": explanation_en,
        "choices": choices,
    }


def m(
    title: str,
    url: str,
    kind: str = "docs",
    description: str = "",
    language: str = "en",
    title_en: str = "",
    description_en: str = "",
) -> dict:
    return {
        "title": title,
        "title_en": title_en,
        "url": url,
        "kind": kind,
        "description": description,
        "description_en": description_en,
        "language": language,
    }
