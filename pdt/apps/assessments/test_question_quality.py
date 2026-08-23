"""Anti-regressão de qualidade dos distratores do teste de admissão.

Opera direto na lista Python do seed (sem DB), igual ao equivalente em
`apps.interviews`. Ver `apps.core.question_quality` para as heurísticas e
os números medidos antes desta correção.
"""
from __future__ import annotations

import importlib.util
import pathlib

from apps.core.question_quality import (
    absolute_leak_rate,
    absolute_word_leaks,
    longest_wins_rate,
    worst_offenders_by_length_gap,
)


def _questions():
    """Carrega QUESTIONS do comando de management sem passar pelo app
    registry do Django nem pelo banco."""
    path = (
        pathlib.Path(__file__).resolve().parent
        / "management"
        / "commands"
        / "seed_admission_test.py"
    )
    spec = importlib.util.spec_from_file_location("seed_admission_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.QUESTIONS


def _pairs(questions):
    out = []
    for q in questions:
        correct = next(c["text"] for c in q["choices"] if c["correct"])
        wrong = [c["text"] for c in q["choices"] if not c["correct"]]
        out.append((correct, wrong))
    return out


def _labeled_pairs(questions):
    return [
        (f"{q['area']}#{i}: {q['statement'][:40]!r}", pair)
        for i, (q, pair) in enumerate(zip(questions, _pairs(questions)))
    ]


class TestSeedListSanity:
    def test_cada_questao_tem_exatamente_uma_correta(self):
        for q in _questions():
            corretas = [c for c in q["choices"] if c["correct"]]
            assert len(corretas) == 1, q["statement"]

    def test_cada_questao_tem_quatro_alternativas(self):
        for q in _questions():
            assert len(q["choices"]) == 4, q["statement"]

    def test_alternativas_sao_unicas_por_questao(self):
        for q in _questions():
            textos = [c["text"] for c in q["choices"]]
            assert len(textos) == len(set(textos)), q["statement"]


class TestDistratoresNaoVazamResposta:
    """A dupla de heurísticas que media o vazamento antes desta correção:
    escolher sempre a mais longa acertava 90,2% no banco do curso, e em
    35,3% das questões um absoluto (apenas/sempre/nunca...) só aparecia nos
    distratores. Aqui o alvo é ficar no nível do chute aleatório (25%) ou
    abaixo, e zero vazamento de absoluto.
    """

    def test_taxa_de_acerto_marcando_sempre_a_mais_longa(self):
        questions = _questions()
        pairs = _pairs(questions)
        taxa = longest_wins_rate(pairs)
        assert taxa <= 0.30, (
            f"Marcar sempre a alternativa mais longa acertaria {taxa * 100:.1f}% "
            f"das questões (baseline aleatório: 25%). Ofensores:\n"
            + "\n".join(worst_offenders_by_length_gap(_labeled_pairs(questions)))
        )

    def test_nenhum_absoluto_vaza_so_no_distrator(self):
        questions = _questions()
        pairs = _pairs(questions)
        taxa = absolute_leak_rate(pairs)
        ofensores = [
            label for label, pair in _labeled_pairs(questions) if absolute_word_leaks(pair)
        ]
        assert taxa == 0.0, (
            f"{taxa * 100:.1f}% das questões têm um absoluto "
            "(apenas/somente/nunca/sempre/...) só no distrator — vira regra "
            f"de prova para descartar a opção errada sem saber o assunto: {ofensores}"
        )
