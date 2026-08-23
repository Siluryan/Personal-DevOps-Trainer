"""Marca a primeira ocorrência de cada termo conhecido no HTML de uma aula.

Usa `html.parser.HTMLParser` (biblioteca padrão, sem dependência nova) para
percorrer o HTML tag por tag e só tocar em texto de fato visível — nunca em
atributo de tag, e nunca dentro de bloco de código (`<pre>`/`<code>`), onde
a sigla é sintaxe, não jargão a explicar.

Cada termo aparece marcado só na primeira vez que surge no texto: marcar
toda ocorrência deixaria o texto poluído de sublinhado pontilhado.
"""
from __future__ import annotations

import re
from html import escape
from html.parser import HTMLParser

from django.core.cache import cache

# Dentro desses elementos o texto é código/atributo, não prosa — nunca marcar ali.
_SKIP_TAGS = frozenset({"pre", "code", "script", "style", "a", "button"})

# Cache do dicionário termo->definição. TTL é rede de segurança; o sinal em
# apps.core.apps.CoreConfig.ready() invalida na hora quando alguém salva ou
# apaga um GlossaryTerm, então a edição pelo admin aparece sem esperar o TTL.
_CACHE_KEY = "core:glossary_terms"
_CACHE_TTL = 300


class _GlossaryAnnotator(HTMLParser):
    def __init__(self, terms: dict[str, str]):
        super().__init__(convert_charrefs=True)
        self._terms = terms
        self._pattern = self._build_pattern(terms) if terms else None
        self._out: list[str] = []
        self._skip_depth = 0
        self._used: set[str] = set()

    @staticmethod
    def _build_pattern(terms: dict[str, str]) -> re.Pattern[str] | None:
        if not terms:
            return None
        # Termos mais longos primeiro: evita que "SOC" case antes de "SOC 2".
        ordered = sorted(terms, key=len, reverse=True)
        alternation = "|".join(re.escape(t) for t in ordered)
        return re.compile(rf"\b(?:{alternation})\b")

    # -- eventos do parser: reemite tag/atributo tal como veio, intocado --
    def handle_starttag(self, tag: str, attrs) -> None:
        self._out.append(self.get_starttag_text() or f"<{tag}>")
        if tag in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._out.append(self.get_starttag_text() or f"<{tag}/>")

    def handle_endtag(self, tag: str) -> None:
        self._out.append(f"</{tag}>")
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")

    # -- único ponto que toca em texto de verdade --
    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0 or self._pattern is None:
            self._out.append(escape(data))
            return
        self._out.append(self._annotate(data))

    def _annotate(self, text: str) -> str:
        pieces: list[str] = []
        last = 0
        for m in self._pattern.finditer(text):
            term = m.group(0)
            pieces.append(escape(text[last:m.start()]))
            last = m.end()
            if term in self._used:
                pieces.append(escape(term))
                continue
            definition = self._terms.get(term)
            if not definition:
                pieces.append(escape(term))
                continue
            self._used.add(term)
            pieces.append(_render_term(term, definition))
        pieces.append(escape(text[last:]))
        return "".join(pieces)

    def get_html(self) -> str:
        return "".join(self._out)


def _render_term(term: str, definition: str) -> str:
    # <span role="button">, não <button> de verdade: um <button> nativo cria uma
    # caixa interna própria que, em vários navegadores, não deixa um filho
    # position:absolute flutuar por cima do texto — o popover acaba empurrando
    # o parágrafo em vez de sobrepor como balão. Span evita esse problema; os
    # atributos abaixo mantêm a mesma acessibilidade de teclado que um <button>.
    safe_term = escape(term)
    safe_def = escape(definition)
    return (
        '<span class="glossary-term" role="button" tabindex="0" '
        'x-data="{ open: false }" '
        '@click="open = !open" @click.outside="open = false" '
        '@keydown.enter="open = !open" @keydown.space.prevent="open = !open" '
        '@keydown.escape="open = false">'
        f"{safe_term}"
        '<span class="glossary-popover" x-show="open" x-cloak @click.stop role="tooltip">'
        f"{safe_def}"
        "</span></span>"
    )


def annotate_glossary_terms(html: str, terms: dict[str, str]) -> str:
    """Retorna `html` com a 1ª ocorrência de cada termo de `terms` marcada.

    `terms` mapeia termo exato (sensível a maiúsculas/minúsculas) -> definição.
    Texto sem nenhum termo conhecido, ou `terms` vazio, volta inalterado.
    """
    if not html or not terms:
        return html or ""
    parser = _GlossaryAnnotator(terms)
    parser.feed(html)
    parser.close()
    return parser.get_html()


def get_glossary_terms() -> dict[str, str]:
    """Termo -> definição de todo `GlossaryTerm`, cacheado (ver `_CACHE_TTL`)."""
    terms = cache.get(_CACHE_KEY)
    if terms is None:
        from .models import GlossaryTerm

        terms = dict(GlossaryTerm.objects.values_list("term", "definition"))
        cache.set(_CACHE_KEY, terms, _CACHE_TTL)
    return terms


def invalidate_glossary_cache(*args, **kwargs) -> None:
    """Conectado a post_save/post_delete de GlossaryTerm em CoreConfig.ready()."""
    cache.delete(_CACHE_KEY)
