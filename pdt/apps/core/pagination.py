"""Divide o corpo longo de uma aula em páginas por seção (`<h3>`).

Aula com 8-12 seções numeradas virando uma rolagem só de 10-15 mil
caracteres é o que gerava a queixa "aula muito longa". Em vez de mudar
como o conteúdo é armazenado (uma string HTML só por `Lesson.body`),
agrupa as seções existentes em páginas de tamanho razoável e deixa a
navegação para o template (client-side, via Alpine.js).

Não depende de reescrever nenhuma das 60 aulas: qualquer corpo que já
usa `<h3>` como divisor de seção (todo o conteúdo da Onda 3) é paginado
automaticamente. Conteúdo sem `<h3>` nenhum simplesmente vira 1 página.
"""
from __future__ import annotations

import re

# Abaixo disso, uma aula cabe numa rolagem razoável e paginar só atrapalharia.
_MIN_CHARS_TO_PAGINATE = 4000

# Alvo de tamanho por página; uma seção sozinha maior que isso vira página
# própria mesmo assim, nunca é cortada no meio.
_TARGET_CHARS_PER_PAGE = 3000

_H3_BOUNDARY_RE = re.compile(r"(?=<h3[ >])")


def paginate_html_sections(
    html: str, target_chars: int = _TARGET_CHARS_PER_PAGE
) -> list[str]:
    """Agrupa `html` em páginas, cada corte acontecendo só antes de um `<h3>`.

    Retorna `[html]` (1 página) quando o conteúdo é curto o suficiente para
    não precisar paginar, ou quando não há `<h3>` para servir de corte.
    """
    if not html or len(html) < _MIN_CHARS_TO_PAGINATE:
        return [html] if html else []

    segments = _H3_BOUNDARY_RE.split(html)
    segments = [s for s in segments if s]
    if len(segments) <= 1:
        return [html]

    pages: list[str] = []
    current: list[str] = []
    current_len = 0

    for segment in segments:
        seg_len = len(segment)
        if current and current_len + seg_len > target_chars:
            pages.append("".join(current))
            current = []
            current_len = 0
        current.append(segment)
        current_len += seg_len

    if current:
        pages.append("".join(current))

    return pages


def paginate_html_sections_like(
    html: str, reference: str, target_chars: int = _TARGET_CHARS_PER_PAGE
) -> list[str]:
    """Pagina `html` copiando o agrupamento de seções que `reference` produz.

    A tradução de uma aula quase nunca tem o mesmo tamanho do original, então
    paginar cada idioma por conta própria dava contagens diferentes de página
    para a MESMA aula (17 dos 60 tópicos). Como o `lesson_page` de cada lab é
    calculado uma vez só, em cima do corpo em português, no inglês o
    exercício caía numa página que ainda não tinha ensinado o assunto — e os
    labs das páginas excedentes não apareciam para ninguém.

    Alinhar pela contagem de seções por página mantém a seção N no mesmo
    número de página nos dois idiomas. Quando as duas versões não têm o mesmo
    número de `<h3>` (tradução reestruturada), não há como alinhar e cada uma
    volta a ser paginada por tamanho.
    """
    if not html:
        return []
    if not reference or reference == html:
        return paginate_html_sections(html, target_chars)

    segments = [s for s in _H3_BOUNDARY_RE.split(html) if s]
    ref_pages = paginate_html_sections(reference, target_chars)
    sizes = [len([s for s in _H3_BOUNDARY_RE.split(p) if s]) for p in ref_pages]
    if sum(sizes) != len(segments):
        return paginate_html_sections(html, target_chars)

    pages: list[str] = []
    start = 0
    for size in sizes:
        pages.append("".join(segments[start : start + size]))
        start += size
    return pages
