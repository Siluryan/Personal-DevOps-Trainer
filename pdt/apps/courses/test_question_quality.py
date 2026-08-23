"""Anti-regressão de qualidade dos distratores das 600 questões do curso.

Ver `apps.core.question_quality` para as heurísticas e o número de partida:
marcar sempre a alternativa mais longa acertava 90,2% do quiz inteiro
(baseline aleatório: 25%), e em 35,3% das questões um absoluto (apenas,
sempre, nunca...) só aparecia nos distratores.

Este arquivo não existia antes — o app `courses` era o único dos três
bancos de questão sem nenhuma rede de qualidade. As 600 questões só
tinham `test_cada_topico_tem_10_questoes_com_unica_correta` e
`test_alternativas_nao_estao_sempre_na_primeira_posicao` (estrutura, não
qualidade de conteúdo) em `apps.courses.tests`.

Os testes de vazamento agregado ficam `xfail` por fase: reescrever 600
distratores é trabalho de conteúdo, não de infraestrutura, e não cabe
misturado com o resto desta correção. Cada `xfail` documenta o número
medido nesta fase; removê-lo é o sinal de que aquela fase foi reescrita.
Ver `apps.assessments.test_question_quality` para um banco pequeno (23
questões) já corrigido com o mesmo par de heurísticas — é o modelo a
seguir fase por fase.
"""
from __future__ import annotations

import pytest

from apps.core.question_quality import (
    absolute_leak_rate,
    absolute_word_leaks,
    longest_wins_rate,
    worst_offenders_by_length_gap,
)
from apps.courses.seed_data import PHASES

# Medido antes desta correção, uma fase por vez.
_BASELINE_LONGEST_WINS = {1: 0.77, 2: 0.89, 3: 0.99, 4: 0.97, 5: 0.97, 6: 0.73}
_TARGET_LONGEST_WINS = 0.30


def _pairs(phase: dict) -> list:
    pairs = []
    for topic in phase["topics"]:
        for q in topic.get("questions", []):
            correct = next(c["text"] for c in q["choices"] if c["correct"])
            wrong = [c["text"] for c in q["choices"] if not c["correct"]]
            pairs.append((correct, wrong))
    return pairs


def _labeled_pairs(phase: dict, phase_num: int) -> list:
    out = []
    for topic in phase["topics"]:
        for i, q in enumerate(topic.get("questions", [])):
            correct = next(c["text"] for c in q["choices"] if c["correct"])
            wrong = [c["text"] for c in q["choices"] if not c["correct"]]
            out.append((f"P{phase_num}/{topic['title'][:30]}#{i}", (correct, wrong)))
    return out


class TestVazamentoAgregadoPorFase:
    @pytest.mark.parametrize("phase_num", [1, 2, 3, 4, 5, 6])
    def test_taxa_de_acerto_marcando_sempre_a_mais_longa(self, phase_num):
        pairs = _pairs(PHASES[phase_num - 1])
        taxa = longest_wins_rate(pairs)
        baseline = _BASELINE_LONGEST_WINS[phase_num]
        if taxa > _TARGET_LONGEST_WINS:
            pytest.xfail(
                f"Onda 3: fase {phase_num} ainda não reescrita "
                f"({taxa * 100:.1f}% marcando sempre a mais longa; "
                f"alvo: ≤ {_TARGET_LONGEST_WINS * 100:.0f}%; "
                f"medição anterior: {baseline * 100:.0f}%)"
            )
        # Se chegou aqui, a fase já foi reescrita — trava para não regredir.
        assert taxa <= _TARGET_LONGEST_WINS, (
            f"Fase {phase_num} regrediu: {taxa * 100:.1f}%.\n"
            + "\n".join(worst_offenders_by_length_gap(_labeled_pairs(PHASES[phase_num - 1], phase_num)))
        )

    @pytest.mark.parametrize("phase_num", [1, 2, 3, 4, 5, 6])
    def test_absoluto_nao_vaza_so_no_distrator(self, phase_num):
        phase = PHASES[phase_num - 1]
        pairs = _pairs(phase)
        taxa = absolute_leak_rate(pairs)
        if taxa > 0.0:
            ofensores = [
                label
                for label, pair in _labeled_pairs(phase, phase_num)
                if absolute_word_leaks(pair)
            ]
            pytest.xfail(
                f"Onda 3: fase {phase_num} — {taxa * 100:.1f}% das questões "
                f"vazam absoluto só no distrator. Exemplos: {ofensores[:5]}"
            )
        assert taxa == 0.0
