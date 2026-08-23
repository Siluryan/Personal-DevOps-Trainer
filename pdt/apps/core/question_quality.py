"""Heurísticas de qualidade de distrator, compartilhadas pelos três bancos de
questão (courses, assessments, interviews).

O defeito que estas heurísticas existem para pegar: quando a alternativa
correta é escrita como uma mini-explicação e os distratores como descarte
rápido, quem não sabe o assunto ainda acerta — não porque reconheceu a
resposta certa, mas porque reconheceu qual das quatro "parece" uma resposta.

Medido nas 600 questões do curso antes desta correção: escolher sempre a
alternativa mais longa acertava 90,2% (baseline aleatório: 25%), e em 35,3%
das questões uma palavra absoluta ("apenas", "sempre", "nunca"...) aparecia
só nos distratores — a regra de prova que todo mundo já conhece.

Cada app normaliza seu formato de questão para `(correta, [distratores])`
antes de chamar estas funções; veja os adaptadores em cada
`test_question_quality.py`.
"""
from __future__ import annotations

import re

Pair = tuple[str, list[str]]

_ABSOLUTE_WORDS_RE = re.compile(
    r"\b(apenas|somente|nunca|sempre|todos|todo|toda|nada|nenhum|nenhuma|"
    r"impossível|obrigatoriamente)\b",
    re.IGNORECASE,
)


def correct_is_longest(pair: Pair) -> bool:
    """True se a correta é (estritamente) a mais longa entre as opções."""
    correct, wrong = pair
    if not wrong:
        return False
    return len(correct) > max(len(w) for w in wrong)


def absolute_word_leaks(pair: Pair) -> bool:
    """True se uma palavra absoluta aparece SÓ nos distratores.

    Não pega o caso oposto (absoluto só na correta) de propósito: a regra de
    prova que os alunos exploram é "descarte a opção com absoluto", que só
    funciona quando a correta é isenta dela.
    """
    correct, wrong = pair
    if _ABSOLUTE_WORDS_RE.search(correct):
        return False
    return any(_ABSOLUTE_WORDS_RE.search(w) for w in wrong)


def _ends_as_sentence(text: str) -> bool:
    """True se `text` termina em ponto final de frase (não reticências)."""
    stripped = text.rstrip()
    return stripped.endswith(".") and not stripped.endswith("...")


def bare_correct_leaks(pair: Pair) -> bool:
    """True se a correta é só o valor "cru" (comando/path/campo, sem pontuação
    de frase no fim) enquanto TODOS os distratores vêm com explicação
    completa (terminam em ponto).

    Pega o giveaway estrutural que sobra depois de igualar tamanho e remover
    palavra absoluta: ex. correta `/etc/passwd`, distratores `/etc/shadow,
    onde o hash de senha fica guardado, legível só pelo root.` — a correta é
    reconhecível por SER a única sem explicação anexada, não por conteúdo.
    """
    correct, wrong = pair
    if not wrong:
        return False
    if _ends_as_sentence(correct):
        return False
    return all(_ends_as_sentence(w) for w in wrong)


def bare_correct_leak_rate(pairs: list[Pair]) -> float:
    if not pairs:
        return 0.0
    return sum(bare_correct_leaks(p) for p in pairs) / len(pairs)


def longest_wins_rate(pairs: list[Pair]) -> float:
    """Acurácia de um aluno que, sem ler o enunciado, sempre marca a mais
    longa. Compare contra o baseline aleatório (1 / nº de alternativas)."""
    if not pairs:
        return 0.0
    return sum(correct_is_longest(p) for p in pairs) / len(pairs)


def absolute_leak_rate(pairs: list[Pair]) -> float:
    if not pairs:
        return 0.0
    return sum(absolute_word_leaks(p) for p in pairs) / len(pairs)


def worst_offenders_by_length_gap(pairs_with_labels: list[tuple[str, Pair]], limit: int = 15) -> list[str]:
    """Formata as piores questões por diferença de tamanho correta-vs-maior-distrator.

    `pairs_with_labels` é uma lista de (rótulo, (correta, distratores)) — o
    rótulo identifica a questão para quem for corrigir (ex.: "P3/Terraform#4").
    """
    scored = []
    for label, (correct, wrong) in pairs_with_labels:
        if not wrong:
            continue
        gap = len(correct) - max(len(w) for w in wrong)
        if gap > 0:
            scored.append((gap, label, correct, wrong))
    scored.sort(reverse=True)
    out = []
    for gap, label, correct, wrong in scored[:limit]:
        maior_distrator = max(wrong, key=len)
        out.append(
            f"  {label}: +{gap}c  ✔({len(correct)}) {correct[:70]!r}  "
            f"✘maior({len(maior_distrator)}) {maior_distrator[:70]!r}"
        )
    return out
