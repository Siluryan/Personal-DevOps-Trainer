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

# Qualquer elemento com esta classe também vira zona proibida (ver
# `_should_skip`): é fonte de diagrama Mermaid, não prosa — marcar um termo
# ali corromperia a sintaxe do diagrama antes do mermaid.js processá-la.
_SKIP_CLASSES = frozenset({"mermaid"})

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
        self._skip_stack: list[str] = []  # nomes de tag que abriram uma zona proibida
        self._used: set[str] = set()
        self.used_order: list[str] = []  # ordem de 1ª aparição, para a sidebar

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
        class_attr = next((v for k, v in attrs if k == "class"), "") or ""
        classes = class_attr.split()
        if tag in _SKIP_TAGS or _SKIP_CLASSES.intersection(classes):
            self._skip_stack.append(tag)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._out.append(self.get_starttag_text() or f"<{tag}/>")

    def handle_endtag(self, tag: str) -> None:
        self._out.append(f"</{tag}>")
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")

    # -- único ponto que toca em texto de verdade --
    def handle_data(self, data: str) -> None:
        if self._skip_stack or self._pattern is None:
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
            self.used_order.append(term)
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
    #
    # `shift`: o popover nasce centralizado no termo (left:50%;
    # translateX(-50%)), o que estoura a viewport quando o termo está perto
    # da borda esquerda ou direita da tela — em mobile isso cria scroll
    # horizontal que só revela o lado direito do balão, nunca o esquerdo
    # (não dá pra "scrollar" pra x negativo). `clampPopover()` mede a
    # posição real depois de abrir e desloca o balão de volta pra dentro
    # da tela, sem depender de reposicionamento manual por termo.
    #
    # Dois requestAnimationFrame em vez de $nextTick: testado ao vivo, o
    # callback de $nextTick roda ANTES do Alpine aplicar de fato o
    # display:block do x-show (a troca de estilo em si é agendada por um
    # microtask separado) — clampPopover media um elemento ainda
    # display:none (rect zerado) e calculava um shift errado. Dois rAF
    # garante que o navegador já pintou o popover visível antes de medir.
    safe_term = escape(term)
    safe_def = escape(definition)
    return (
        '<span class="glossary-term" role="button" tabindex="0" '
        'x-data="{ open: false, shift: 0, '
        "toggle() { this.open = !this.open; if (this.open) { this.shift = 0; "
        "requestAnimationFrame(() => requestAnimationFrame(() => this.clampPopover())); } }, "
        "clampPopover() { const el = this.$refs.pop; if (!el) return; "
        "const margin = 8; const rect = el.getBoundingClientRect(); "
        "if (rect.left < margin) { this.shift = margin - rect.left; } "
        "else if (rect.right > window.innerWidth - margin) { this.shift = (window.innerWidth - margin) - rect.right; } "
        '} }" '
        '@click="toggle()" @click.outside="open = false" '
        '@keydown.enter="toggle()" @keydown.space.prevent="toggle()" '
        '@keydown.escape="open = false">'
        f"{safe_term}"
        '<span class="glossary-popover" x-ref="pop" x-show="open" x-cloak @click.stop role="tooltip" '
        ':style="`transform: translateX(calc(-50% + ${shift}px))`">'
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


def lesson_glossary_sidebar(html_parts: list[str], terms: dict[str, str], limit: int = 12) -> list[dict[str, str]]:
    """Termos do glossário citados em uma aula, em ordem de 1ª aparição.

    `html_parts` é a lista de blocos de HTML da aula (intro, corpo, prático),
    concatenados aqui para que a ordem reflita a leitura de cima a baixo,
    mesmo com o corpo paginado em pedaços menores em `paginate_lesson_body`.
    Serve para montar a sidebar "Nesta aula" ao lado do conteúdo. Respeita o
    mesmo `_SKIP_TAGS` do popover inline: nunca cita termo que só aparece
    dentro de bloco de código.
    """
    if not terms:
        return []
    combined = "\n".join(part for part in html_parts if part)
    if not combined:
        return []
    parser = _GlossaryAnnotator(terms)
    parser.feed(combined)
    parser.close()
    return [
        {"term": term, "definition": terms[term]}
        for term in parser.used_order[:limit]
    ]


def get_glossary_terms() -> dict[str, str]:
    """Termo -> definição de todo `GlossaryTerm`, cacheado (ver `_CACHE_TTL`).

    Uma entrada por idioma ativo: em inglês, a CHAVE também precisa virar
    `term_en` (ou ficar em `term` se a sigla não muda, tipo RCE/IAM), porque
    o texto que o `_GlossaryAnnotator` varre é o `Lesson.display_body`, que
    já está em inglês — procurar pela grafia em português nunca bateria.
    """
    from django.utils.translation import get_language

    lang = get_language()
    cache_key = f"{_CACHE_KEY}:{lang}"
    terms = cache.get(cache_key)
    if terms is None:
        from .models import GlossaryTerm

        rows = GlossaryTerm.objects.values_list("term", "term_en", "definition", "definition_en")
        if lang == "en":
            terms = {(en or pt): (def_en or pt_def) for pt, en, pt_def, def_en in rows}
        else:
            terms = {pt: pt_def for pt, _en, pt_def, _def_en in rows}
        cache.set(cache_key, terms, _CACHE_TTL)
    return terms


def invalidate_glossary_cache(*args, **kwargs) -> None:
    """Conectado a post_save/post_delete de GlossaryTerm em CoreConfig.ready()."""
    cache.delete(f"{_CACHE_KEY}:pt-br")
    cache.delete(f"{_CACHE_KEY}:en")
