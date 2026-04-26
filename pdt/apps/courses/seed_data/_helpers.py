"""Helpers para construir entradas de questão de forma compacta."""
from __future__ import annotations

import random


def q(statement: str, correct: str, wrong: list[str], explanation: str = "") -> dict:
    """Cria uma questão de múltipla escolha (1 correta + N erradas).

    As alternativas são embaralhadas para que a correta não esteja sempre
    na primeira posição, o embaralhamento ocorre no momento do seed.
    """
    choices = [{"text": correct, "correct": True}]
    for w in wrong:
        choices.append({"text": w, "correct": False})
    random.shuffle(choices)
    return {
        "statement": statement,
        "explanation": explanation,
        "choices": choices,
    }


def m(title: str, url: str, kind: str = "docs", description: str = "", language: str = "en") -> dict:
    return {
        "title": title,
        "url": url,
        "kind": kind,
        "description": description,
        "language": language,
    }
