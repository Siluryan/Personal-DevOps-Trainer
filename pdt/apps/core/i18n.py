"""Escolha de conteúdo bilíngue para os modelos com campos `*_en`.

O site tem UM idioma de interface (via Django i18n / LocaleMiddleware,
alternado pelo botão em `_lang_switch.html`) e, separadamente, conteúdo de
banco (aula, questão, lab, termo de glossário) que também pode ter uma
versão em inglês guardada num campo irmão `*_en`. `localized()` decide qual
mostrar: some para o inglês só se `get_language()` for "en" E o campo `*_en`
já tiver sido preenchido — enquanto a tradução de um campo não existir,
cai de volta pro português, nunca mostra vazio.
"""
from __future__ import annotations

from django.utils.translation import get_language


def localized(pt_value, en_value):
    if get_language() == "en" and en_value:
        return en_value
    return pt_value
