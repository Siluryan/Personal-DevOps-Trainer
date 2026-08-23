"""Testes da paginação de aula longa por seção (`<h3>`).

Cobre a queixa original "sem paginação para aulas longas".
"""
from __future__ import annotations

import pytest
from django.core.cache import cache

from apps.core.models import GlossaryTerm
from apps.core.pagination import (
    _MIN_CHARS_TO_PAGINATE,
    _TARGET_CHARS_PER_PAGE,
    paginate_html_sections,
)
from apps.core.templatetags.pdt_extras import paginate_lesson_body


def _h3_section(n: int, filler_chars: int) -> str:
    return f"<h3>{n}. Seção</h3><p>{'x' * filler_chars}</p>"


class TestPaginateHtmlSections:
    def test_conteudo_curto_vira_1_pagina(self):
        html = "<p>texto curto</p>"
        assert paginate_html_sections(html) == [html]

    def test_conteudo_longo_sem_h3_vira_1_pagina(self):
        html = "<p>" + ("x" * (_MIN_CHARS_TO_PAGINATE + 500)) + "</p>"
        assert paginate_html_sections(html) == [html]

    def test_vazio_retorna_lista_vazia(self):
        assert paginate_html_sections("") == []
        assert paginate_html_sections(None) == []

    def test_agrupa_secoes_ate_o_alvo_de_tamanho(self):
        # Total precisa passar de _MIN_CHARS_TO_PAGINATE para não virar 1 página só.
        secoes = [_h3_section(i, 1200) for i in range(1, 5)]
        html = "".join(secoes)
        pages = paginate_html_sections(html, target_chars=700)
        assert len(pages) >= 2
        # Nenhuma seção foi cortada no meio: cada página começa com <h3>.
        for page in pages:
            assert page.startswith("<h3")

    def test_secao_maior_que_o_alvo_vira_pagina_propria_sem_cortar(self):
        secoes = [_h3_section(1, 100), _h3_section(2, 5000), _h3_section(3, 100)]
        html = "".join(secoes)
        pages = paginate_html_sections(html, target_chars=1000)
        # A seção 2 (5000 chars) não pode ter sido dividida em duas páginas.
        secao_2_paginas = [p for p in pages if "2. Seção" in p]
        assert len(secao_2_paginas) == 1
        assert "x" * 5000 in secao_2_paginas[0]

    def test_reconstituicao_preserva_conteudo_original(self):
        secoes = [_h3_section(i, 800) for i in range(1, 8)]
        html = "".join(secoes)
        pages = paginate_html_sections(html, target_chars=1200)
        assert len(pages) > 1  # garante que passou pelo caminho de agrupamento de verdade
        assert "".join(pages) == html

    def test_conteudo_antes_do_primeiro_h3_fica_na_primeira_pagina(self):
        html = "<p>intro sem seção</p>" + "".join(
            _h3_section(i, 1200) for i in range(1, 5)
        )
        pages = paginate_html_sections(html, target_chars=1500)
        assert len(pages) > 1  # garante que passou pelo caminho de agrupamento de verdade
        assert pages[0].startswith("<p>intro sem seção</p>")

    def test_default_target_e_razoavel(self):
        # Sanidade: o alvo default não é absurdamente pequeno nem gigante.
        assert 1000 <= _TARGET_CHARS_PER_PAGE <= 6000


@pytest.mark.django_db
class TestPaginateLessonBodyFilter:
    def setup_method(self):
        cache.clear()

    def test_corpo_curto_vira_lista_de_1_pagina(self):
        pages = paginate_lesson_body("<p>corpo curto</p>")
        assert len(pages) == 1

    def test_glossario_e_marcado_antes_de_paginar(self):
        GlossaryTerm.objects.create(term="RCE", definition="Remote Code Execution.")
        secoes = "".join(_h3_section(i, 1600) for i in range(1, 6))
        html = f"<p>Um ataque de RCE aqui.</p>{secoes}"
        pages = paginate_lesson_body(html)
        assert len(pages) > 1
        junto = "".join(str(p) for p in pages)
        assert junto.count("glossary-term") == 1  # 1ª ocorrência só, mesmo cruzando páginas

    def test_corpo_vazio_vira_lista_vazia(self):
        assert paginate_lesson_body("") == []
