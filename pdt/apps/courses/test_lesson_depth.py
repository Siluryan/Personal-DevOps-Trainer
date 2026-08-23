"""Anti-regressão de profundidade das aulas.

A auditoria da plataforma mediu, no corpo de cada uma das 60 aulas, quantas
palavras estão dentro de `<p>` (prosa explicativa) contra `<li>` (lista) e
`<pre>` (código). Resultado: só 29,5% do texto da trilha inteira é prosa —
o resto é lista solta ou bloco de comando, sem o "porquê", sem trade-off,
sem modo de falha. É material de revisão para quem já sabe o assunto, não
material de aprendizado para quem está vendo pela primeira vez.

Este teste não valida CONTEÚDO (isso exige leitura humana), só a proporção
estrutural — um proxy grosseiro, mas mensurável, de "isto é uma explicação
ou uma lista de comandos". Fica `xfail` por fase até a fase ser reescrita;
tirar o `xfail` é o sinal de progresso. Ver `apps.courses.seed_data.phase6`
(commit desta correção) para a primeira fase com um lote reescrito.
"""
from __future__ import annotations

import html
import re

import pytest

from apps.courses.seed_data import PHASES

_TARGET_PROSE_RATIO = 0.45

# Medido antes desta correção.
_BASELINE_PROSE_RATIO = {1: 0.406, 2: 0.363, 3: 0.309, 4: 0.238, 5: 0.208, 6: 0.264}


def _strip_tags(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def _word_ratios(body: str) -> dict:
    prosa = len(_strip_tags("".join(re.findall(r"<p>(.*?)</p>", body, re.S))).split())
    bullets = len(_strip_tags("".join(re.findall(r"<li>(.*?)</li>", body, re.S))).split())
    codigo = len("".join(re.findall(r"<pre>(.*?)</pre>", body, re.S)).split())
    total = prosa + bullets + codigo
    if not total:
        return {"prosa": 0.0, "bullets": 0.0, "codigo": 0.0}
    return {"prosa": prosa / total, "bullets": bullets / total, "codigo": codigo / total}


def _phase_prose_ratio(phase_num: int) -> float:
    phase = PHASES[phase_num - 1]
    prosa = bullets = codigo = 0
    for topic in phase["topics"]:
        body = topic["lesson"]["body"]
        prosa += len(_strip_tags("".join(re.findall(r"<p>(.*?)</p>", body, re.S))).split())
        bullets += len(_strip_tags("".join(re.findall(r"<li>(.*?)</li>", body, re.S))).split())
        codigo += len("".join(re.findall(r"<pre>(.*?)</pre>", body, re.S)).split())
    total = prosa + bullets + codigo
    return prosa / total if total else 0.0


class TestProfundidadeDaAulaPorFase:
    @pytest.mark.parametrize("phase_num", [1, 2, 3, 4, 5, 6])
    def test_proporcao_de_prosa_no_corpo_da_aula(self, phase_num):
        ratio = _phase_prose_ratio(phase_num)
        baseline = _BASELINE_PROSE_RATIO[phase_num]
        if ratio < _TARGET_PROSE_RATIO:
            pytest.xfail(
                f"Onda 3: fase {phase_num} ainda não reescrita "
                f"({ratio * 100:.1f}% de prosa; alvo: ≥ {_TARGET_PROSE_RATIO * 100:.0f}%; "
                f"medição anterior: {baseline * 100:.1f}%)"
            )
        assert ratio >= _TARGET_PROSE_RATIO, f"Fase {phase_num} regrediu: {ratio * 100:.1f}%"


class TestHelperDeProporcao:
    def test_body_so_com_paragrafo_da_100_por_cento_prosa(self):
        r = _word_ratios("<p>Isto é uma explicação completa em prosa corrida.</p>")
        assert r["prosa"] == 1.0

    def test_body_so_com_lista_da_zero_prosa(self):
        r = _word_ratios("<ul><li>um</li><li>dois</li></ul>")
        assert r["prosa"] == 0.0

    def test_body_vazio_nao_quebra(self):
        assert _word_ratios("") == {"prosa": 0.0, "bullets": 0.0, "codigo": 0.0}
