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
    paginate_html_sections_like,
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

    def test_glossario_marca_so_a_1a_ocorrencia_da_aula_inteira(self):
        GlossaryTerm.objects.create(term="RCE", definition="Remote Code Execution.")
        secoes = "".join(f"<h3>{i}. RCE</h3><p>{'x' * 1600}</p>" for i in range(1, 6))
        html = f"<p>Um ataque de RCE aqui.</p>{secoes}"
        pages = paginate_lesson_body(html)
        assert len(pages) > 1
        junto = "".join(str(p) for p in pages)
        assert junto.count("glossary-term") == 1  # 1ª ocorrência só, mesmo cruzando páginas

    def test_glossario_nao_muda_onde_a_pagina_corta(self):
        """Markup do popover não pode empurrar seção para a página seguinte.

        O popover custa ~1,2 mil caracteres por termo — anotar antes de
        paginar inflava o corpo e rendia mais páginas que o seed calcula
        para decidir o `lesson_page` do lab, que então aparecia numa página
        cujo assunto a aula ainda nem tinha apresentado.
        """
        GlossaryTerm.objects.create(term="RCE", definition="Remote Code Execution.")
        secoes = "".join(f"<h3>{i}. RCE</h3><p>{'x' * 1200}</p>" for i in range(1, 7))
        sem_glossario = paginate_html_sections(secoes)
        pages = paginate_lesson_body(secoes)
        assert len(pages) == len(sem_glossario)
        for page, cru in zip(pages, sem_glossario):
            assert str(page).count("<h3") == cru.count("<h3")

    def test_traducao_pagina_igual_ao_corpo_de_referencia(self):
        # O `lesson_page` do lab sai do corpo em português; o inglês precisa
        # cortar nas mesmas seções mesmo sendo bem mais curto.
        pt = "".join(_h3_section(i, 1400) for i in range(1, 7))
        en = "".join(_h3_section(i, 90) for i in range(1, 7))
        pages_pt = paginate_lesson_body(pt, pt)
        pages_en = paginate_lesson_body(en, pt)
        assert len(pages_pt) > 1
        assert len(pages_en) == len(pages_pt)
        for page_en, page_pt in zip(pages_en, pages_pt):
            assert str(page_en).count("<h3") == str(page_pt).count("<h3")

    def test_corpo_vazio_vira_lista_vazia(self):
        assert paginate_lesson_body("") == []


class TestPaginateHtmlSectionsLike:
    """Sem banco: a função é pura."""

    def test_sem_referencia_cai_na_paginacao_por_tamanho(self):
        html = "".join(_h3_section(i, 1200) for i in range(1, 6))
        assert paginate_html_sections_like(html, "") == paginate_html_sections(html)

    def test_copia_o_agrupamento_da_referencia(self):
        ref = "".join(_h3_section(i, 1400) for i in range(1, 7))
        curto = "".join(_h3_section(i, 60) for i in range(1, 7))
        esperado = [p.count("<h3") for p in paginate_html_sections(ref)]
        pages = paginate_html_sections_like(curto, ref)
        assert [p.count("<h3") for p in pages] == esperado

    def test_numero_de_secoes_diferente_volta_a_paginar_por_tamanho(self):
        ref = "".join(_h3_section(i, 1400) for i in range(1, 7))
        outro = "".join(_h3_section(i, 1400) for i in range(1, 4))
        assert paginate_html_sections_like(outro, ref) == paginate_html_sections(outro)

    def test_preserva_o_conteudo_original(self):
        ref = "".join(_h3_section(i, 1400) for i in range(1, 7))
        curto = "".join(_h3_section(i, 60) for i in range(1, 7))
        assert "".join(paginate_html_sections_like(curto, ref)) == curto

    def test_vazio_retorna_lista_vazia(self):
        assert paginate_html_sections_like("", "qualquer") == []
