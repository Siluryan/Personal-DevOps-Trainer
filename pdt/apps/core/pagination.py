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
