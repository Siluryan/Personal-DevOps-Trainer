"""Mede o vazamento por FORMA das alternativas, em todos os bancos de questão.

Uso:
    python3 scripts/check_question_balance.py              # tudo
    python3 scripts/check_question_balance.py curso        # só o curso
    python3 scripts/check_question_balance.py entrevistas  # só as entrevistas
    python3 scripts/check_question_balance.py curso 2 --piores

Não precisa de Django nem de banco: lê `apps/*/seed_data`.

O que mede é quanto um aluno acerta SEM LER o enunciado, só escolhendo pela
forma da alternativa. Baseline aleatório com 4 opções: 25%.

As duas taxas (mais longa / mais curta) contam, porque o viés vale nos dois
sentidos e corrigir um lado empurra o problema para o outro — foi o que
aconteceu duas vezes neste projeto: "mais longa" caiu de 90,2% para 3,5% e
"mais curta" subiu para 77,2%; depois, ao remover o enchimento dos
distratores das entrevistas, "mais curta" caiu de 87% para 1% e "mais
longa" subiu para 53%.

PT e EN são medidos separadamente de propósito: a plataforma tem toggle de
idioma, o aluno em inglês lê os campos `*_en`, e já houve o caso de o PT ser
limpo e o EN seguir com as mesmas caudas de enchimento.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apps.core.question_quality import (  # noqa: E402
    absolute_leak_rate,
    bare_correct_leak_rate,
    correct_is_longest,
    correct_is_shortest,
    longest_wins_rate,
    shortest_wins_rate,
)
from apps.courses.seed_data import PHASES  # noqa: E402
from apps.interviews.seed_data import ALL_INTERVIEW_QUESTIONS  # noqa: E402

TARGET = 0.30
Pair = tuple[str, list[str]]


def _course_pairs(phase: dict, lang: str) -> list[Pair]:
    key = "text" if lang == "pt" else "text_en"
    out = []
    for topic in phase["topics"]:
        for q in topic.get("questions", []):
            correct = next((c.get(key) for c in q["choices"] if c["correct"]), None)
            wrong = [c.get(key) for c in q["choices"] if not c["correct"]]
            if correct and all(wrong):
                out.append((correct, wrong))
    return out


def _interview_pairs(questions: list[dict], lang: str) -> list[Pair]:
    out = []
    for q in questions:
        choices = q["choices"] if lang == "pt" else q.get("choices_en")
        if not choices or len(choices) != len(q["choices"]):
            continue
        i = q["correct_index"]
        out.append((choices[i], [c for j, c in enumerate(choices) if j != i]))
    return out


def _worst(pairs_with_labels: list[tuple[str, Pair]], limit: int = 12) -> list[str]:
    rows = []
    for label, (correct, wrong) in pairs_with_labels:
        if correct_is_shortest((correct, wrong)):
            gap = min(len(w) for w in wrong) - len(correct)
            rows.append((gap, "curta", label, correct, sorted(len(w) for w in wrong)))
        elif correct_is_longest((correct, wrong)):
            gap = len(correct) - max(len(w) for w in wrong)
            rows.append((gap, "longa", label, correct, sorted(len(w) for w in wrong)))
    rows.sort(reverse=True)
    return [
        f"  folga {g:>3} ({kind}) [{lbl[:26]}] correta({len(c)}): {c[:56]}\n"
        f"            distratores: {lens}"
        for g, kind, lbl, c, lens in rows[:limit]
    ]


def _report(name: str, pairs: list[Pair], labeled, show_worst: bool) -> bool:
    if not pairs:
        print(f"{name:24} (sem dados)")
        return True
    longest = longest_wins_rate(pairs)
    shortest = shortest_wins_rate(pairs)
    absolute = absolute_leak_rate(pairs)
    bare = bare_correct_leak_rate(pairs)
    ok = longest <= TARGET and shortest <= TARGET and absolute == 0 and bare == 0
    print(
        f"{name:24} {'OK  ' if ok else 'RUIM'} | "
        f"mais-longa {longest * 100:5.1f}% | mais-curta {shortest * 100:5.1f}% | "
        f"absoluto {absolute * 100:4.1f}% | correta-crua {bare * 100:4.1f}%"
    )
    if show_worst and not ok and labeled:
        print("\n".join(_worst(labeled)))
    return ok


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_worst = "--piores" in sys.argv
    scope = next((a for a in argv if not a.isdigit()), None)
    nums = [int(a) for a in argv if a.isdigit()] or [1, 2, 3, 4, 5, 6]

    results = []
    if scope in (None, "curso"):
        for n in nums:
            phase = PHASES[n - 1]
            for lang in ("pt", "en"):
                pairs = _course_pairs(phase, lang)
                labeled = [
                    (f"{t['title']}#{i}", p)
                    for t in phase["topics"]
                    for i, p in enumerate(_course_pairs({"topics": [t]}, lang))
                ]
                results.append(_report(f"curso fase {n} [{lang}]", pairs, labeled, show_worst))
    if scope in (None, "entrevistas"):
        for lvl, qs in ALL_INTERVIEW_QUESTIONS.items():
            for lang in ("pt", "en"):
                pairs = _interview_pairs(qs, lang)
                labeled = [(f"{lvl}#{i}", p) for i, p in enumerate(pairs)]
                results.append(_report(f"entrevista {lvl} [{lang}]", pairs, labeled, show_worst))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
