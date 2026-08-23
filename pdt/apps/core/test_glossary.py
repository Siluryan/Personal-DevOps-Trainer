"""Testes do glossário clicável: anotação de HTML, cache e integração com render_lesson.

Cobre a queixa original "termos técnicos usados sem explicação" (RCE, IAM,
etc. aparecendo nas aulas sem nunca serem definidos).
"""
from __future__ import annotations

import pytest
from django.core.cache import cache
from django.core.management import call_command

from apps.core.glossary import annotate_glossary_terms, get_glossary_terms, lesson_glossary_sidebar
from apps.core.models import GlossaryTerm
from apps.core.templatetags.pdt_extras import render_lesson


class TestAnnotateGlossaryTerms:
    """`annotate_glossary_terms` é pura (sem banco): não precisa de `db`."""

    def test_marca_primeira_ocorrencia(self):
        html = "<p>Um ataque de RCE explora uma falha.</p>"
        out = annotate_glossary_terms(html, {"RCE": "Remote Code Execution."})
        assert 'class="glossary-term"' in out
        assert "Remote Code Execution." in out
        assert ">RCE<" in out  # o termo em si continua visível dentro do botão

    def test_nao_marca_segunda_ocorrencia_do_mesmo_termo(self):
        html = "<p>RCE aqui, e RCE de novo ali.</p>"
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert out.count('class="glossary-term"') == 1

    def test_nao_marca_dentro_de_bloco_de_codigo(self):
        html = "<pre><code>echo RCE_TOKEN</code></pre>"
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert "glossary-term" not in out
        assert "echo RCE_TOKEN" in out

    def test_nao_marca_dentro_de_link(self):
        html = "<p><a href='/x'>Link com RCE dentro</a></p>"
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert "glossary-term" not in out

    def test_nao_marca_dentro_de_diagrama_mermaid(self):
        # Fonte de diagrama Mermaid é sintaxe, não prosa — marcar um termo ali
        # corromperia o texto que o mermaid.js precisa parsear no navegador.
        html = (
            '<p>TCP usa handshake.</p>'
            '<div class="mermaid">sequenceDiagram\n  A->>B: TCP SYN</div>'
            '<p>De novo TCP aqui fora.</p>'
        )
        out = annotate_glossary_terms(html, {"TCP": "Protocolo confiável."})
        mermaid_block = out.split('<div class="mermaid">')[1].split("</div>")[0]
        assert "glossary-term" not in mermaid_block
        assert out.count("glossary-term") == 1  # só a 1ª ocorrência fora do diagrama

    def test_termo_com_case_diferente_nao_bate(self):
        # Casamento é sensível a maiúsculas/minúsculas de propósito (evita falso
        # positivo em palavra comum que coincide com uma sigla em minúsculo).
        html = "<p>rce em minúsculo não é a sigla.</p>"
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert "glossary-term" not in out

    def test_entidades_html_sobrevivem_ao_roundtrip(self):
        html = "<p>A &amp; B causam RCE.</p>"
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert "&amp;" in out

    def test_sem_termos_retorna_inalterado(self):
        html = "<p>nada aqui</p>"
        assert annotate_glossary_terms(html, {}) == html

    def test_entrada_vazia(self):
        assert annotate_glossary_terms("", {"RCE": "def"}) == ""


class TestLessonGlossarySidebar:
    """`lesson_glossary_sidebar` monta a lista da sidebar "Nesta aula" (sem banco)."""

    TERMS = {
        "RTT": "Round-Trip Time.",
        "QUIC": "Protocolo moderno sobre UDP.",
        "TCP": "Protocolo confiável.",
    }

    def test_ordem_e_por_1a_aparicao_entre_os_blocos(self):
        intro = "<p>Handshake tradicional usa TCP.</p>"
        body = "<p>RTT antes do byte. QUIC roda sobre UDP. De novo: RTT e TCP.</p>"
        result = lesson_glossary_sidebar([intro, body, None], self.TERMS)
        assert [item["term"] for item in result] == ["TCP", "RTT", "QUIC"]

    def test_sem_duplicata_mesmo_citado_em_blocos_diferentes(self):
        intro = "<p>TCP aqui.</p>"
        practical = "<p>TCP de novo aqui.</p>"
        result = lesson_glossary_sidebar([intro, None, practical], self.TERMS)
        assert len(result) == 1

    def test_respeita_limit(self):
        body = "<p>RTT, QUIC e TCP juntos.</p>"
        result = lesson_glossary_sidebar([None, body, None], self.TERMS, limit=2)
        assert len(result) == 2

    def test_ignora_termo_dentro_de_bloco_de_codigo(self):
        body = "<pre><code>RTT = 40</code></pre><p>Sem menção fora do código.</p>"
        result = lesson_glossary_sidebar([None, body, None], self.TERMS)
        assert result == []

    def test_sem_termos_conhecidos_retorna_lista_vazia(self):
        assert lesson_glossary_sidebar(["<p>nada aqui</p>"], {}) == []

    def test_todos_blocos_vazios_retorna_lista_vazia(self):
        assert lesson_glossary_sidebar([None, "", None], self.TERMS) == []
        assert annotate_glossary_terms(None, {"RCE": "def"}) == ""

    def test_atributo_de_tag_nunca_e_tocado(self):
        html = '<p title="RCE">texto normal</p>'
        out = annotate_glossary_terms(html, {"RCE": "def"})
        assert 'title="RCE"' in out
        assert "glossary-term" not in out


@pytest.mark.django_db
class TestGetGlossaryTerms:
    def setup_method(self):
        cache.clear()

    def test_busca_termos_do_banco(self):
        GlossaryTerm.objects.create(term="IAM", definition="Identity and Access Management.")
        terms = get_glossary_terms()
        assert terms == {"IAM": "Identity and Access Management."}

    def test_cache_invalidado_ao_salvar(self):
        term = GlossaryTerm.objects.create(term="IAM", definition="v1")
        assert get_glossary_terms()["IAM"] == "v1"

        term.definition = "v2"
        term.save(update_fields=["definition"])

        assert get_glossary_terms()["IAM"] == "v2"

    def test_cache_invalidado_ao_apagar(self):
        term = GlossaryTerm.objects.create(term="IAM", definition="v1")
        assert "IAM" in get_glossary_terms()

        term.delete()

        assert "IAM" not in get_glossary_terms()


@pytest.mark.django_db
class TestRenderLessonComGlossario:
    def setup_method(self):
        cache.clear()

    def test_render_lesson_marca_termo_conhecido(self):
        GlossaryTerm.objects.create(term="RCE", definition="Remote Code Execution.")
        out = render_lesson("<p>Um ataque de RCE aqui.</p>")
        assert "glossary-term" in out
        assert "Remote Code Execution." in out

    def test_render_lesson_sem_glossario_funciona_normalmente(self):
        out = render_lesson("<p>Texto sem sigla nenhuma.</p>")
        assert "glossary-term" not in out
        assert "Texto sem sigla nenhuma." in out

    def test_render_lesson_texto_puro_ainda_vira_paragrafo(self):
        out = render_lesson("texto simples sem html")
        assert "<p>" in out


@pytest.mark.django_db
class TestSeedGlossary:
    def test_seed_glossary_cria_termos(self):
        call_command("seed_glossary", verbosity=0)
        assert GlossaryTerm.objects.count() > 0
        assert GlossaryTerm.objects.filter(term="RCE").exists()

    def test_seed_glossary_idempotente(self):
        call_command("seed_glossary", verbosity=0)
        total_1 = GlossaryTerm.objects.count()
        call_command("seed_glossary", verbosity=0)
        assert GlossaryTerm.objects.count() == total_1

    def test_seed_glossary_preserva_edicao_do_admin(self):
        call_command("seed_glossary", verbosity=0)
        termo = GlossaryTerm.objects.get(term="RCE")
        termo.definition = "definição customizada pelo admin"
        termo.seed_managed = False
        termo.save(update_fields=["definition", "seed_managed"])

        call_command("seed_glossary", verbosity=0)

        termo.refresh_from_db()
        assert termo.definition == "definição customizada pelo admin"

    def test_seed_glossary_force_sobrescreve_edicao(self):
        call_command("seed_glossary", verbosity=0)
        termo = GlossaryTerm.objects.get(term="RCE")
        original_definition = termo.definition
        termo.definition = "definição customizada pelo admin"
        termo.seed_managed = False
        termo.save(update_fields=["definition", "seed_managed"])

        call_command("seed_glossary", force=True, verbosity=0)

        termo.refresh_from_db()
        assert termo.definition == original_definition
        assert termo.seed_managed is True
