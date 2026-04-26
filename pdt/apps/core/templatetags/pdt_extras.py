"""Filtros de template customizados do PDT."""
from django import template
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def render_lesson(value: str) -> str:
    """Renderiza campo de aula.

    - Se o conteúdo já contém HTML (começa com '<'), retorna como safe diretamente.
    - Caso contrário, aplica `linebreaks` (texto puro → <p>) e retorna safe.
    """
    if not value:
        return ""
    stripped = value.strip()
    if stripped.startswith("<"):
        return mark_safe(stripped)
    return mark_safe(linebreaks(stripped))


@register.filter
def get_item(dictionary, key):
    """Retorna dictionary[key], ou None se não existir.

    Uso no template: {{ scores|get_item:topic.id }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def points_of(score_obj) -> int:
    """Retorna o número de pontos de um objeto TopicScore (ou 0 se None).

    Uso no template: {{ score|points_of }}
    """
    if score_obj is None:
        return 0
    return getattr(score_obj, "points", 0)
