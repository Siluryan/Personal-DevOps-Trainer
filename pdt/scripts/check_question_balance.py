"""Mede o vazamento por FORMA das alternativas, fase por fase.

Uso:
    python3 scripts/check_question_balance.py            # todas as fases
    python3 scripts/check_question_balance.py 2          # só a fase 2
    python3 scripts/check_question_balance.py 2 --piores # + as questões ruins

Não precisa de Django nem de banco: lê `apps/courses/seed_data`.

O que ele mede é quanto um aluno acerta SEM LER o enunciado, só escolhendo
pela forma da alternativa. Baseline aleatório com 4 opções: 25%. As duas
taxas (mais longa / mais curta) precisam ficar em ≤ 30%: o viés vale nos
dois sentidos, e corrigir só um lado empurra o problema para o outro — foi
o que aconteceu quando "mais longa" caiu de 90,2% para 3,5% e "mais curta"
subiu para 77,2%.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apps.core.question_quality import (  # noqa: E402
    absolute_leak_rate,
    bare_correct_leak_rate,
    correct_is_shortest,
    longest_wins_rate,
    shortest_wins_rate,
)
from apps.courses.seed_data import PHASES  # noqa: E402

TARGET = 0.30


def pairs_of(phase: dict) -> list[tuple[str, list[str]]]:
    out = []
    for topic in phase["topics"]:
        for q in topic.get("questions", []):
            correct = next(c["text"] for c in q["choices"] if c["correct"])
            wrong = [c["text"] for c in q["choices"] if not c["correct"]]
            out.append((correct, wrong))
    return out


def worst(phase: dict, limit: int = 12) -> list[str]:
    rows = []
    for topic in phase["topics"]:
        for q in topic.get("questions", []):
            correct = next(c["text"] for c in q["choices"] if c["correct"])
            wrong = [c["text"] for c in q["choices"] if not c["correct"]]
            gap = min(len(w) for w in wrong) - len(correct)
            if correct_is_shortest((correct, wrong)):
                rows.append((gap, topic["title"], correct, sorted(len(w) for w in wrong)))
    rows.sort(reverse=True)
    return [
        f"  folga {g:>3}  [{t[:28]}] correta({len(c)}): {c[:58]}\n"
        f"            distratores: {lens}"
        for g, t, c, lens in rows[:limit]
    ]


def report(num: int, show_worst: bool) -> bool:
    phase = PHASES[num - 1]
    pairs = pairs_of(phase)
    longest = longest_wins_rate(pairs)
    shortest = shortest_wins_rate(pairs)
    absolute = absolute_leak_rate(pairs)
    bare = bare_correct_leak_rate(pairs)
    ok = longest <= TARGET and shortest <= TARGET and absolute == 0 and bare == 0
    print(
        f"fase {num}: {'OK ' if ok else 'RUIM'} | "
        f"mais-longa {longest * 100:5.1f}% | mais-curta {shortest * 100:5.1f}% | "
        f"absoluto {absolute * 100:4.1f}% | correta-crua {bare * 100:4.1f}%"
    )
    if show_worst and not ok:
        print("\n".join(worst(phase)))
    return ok


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_worst = "--piores" in sys.argv
    nums = [int(a) for a in args] if args else [1, 2, 3, 4, 5, 6]
    return 0 if all([report(n, show_worst) for n in nums]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
