"""Testes anti-regressão de templates.

Cobrem duas classes de bugs descobertos na prática:

1. **Anti-pattern do Alpine.js**: quando um elemento tem ao mesmo tempo
   `style="..."` (estático) e `x-bind:style` (ou seu shorthand `:style`),
   o valor do bind precisa ser um **objeto** (`{ background: ..., color: ... }`).
   Se for uma **string** literal, o Alpine **substitui** o `style` inteiro
   em vez de mesclar, apagando `display:flex`, `width`, `padding` etc.
   Esse foi o bug que fez as alternativas das entrevistas aparecerem todas
   na mesma linha e o item selecionado do leaderboard perder o `flex`.

2. **Layout das alternativas do simulador (`take.html`)**: as alternativas
   precisam ficar empilhadas (uma embaixo da outra) com o card inteiro
   clicável, não dependendo de classes Tailwind do CDN para isso.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from django.urls import reverse


# ─────────────────────────────────────────────────────────────────────────
# 1) Anti-pattern Alpine.js: `:style` / `x-bind:style` em string + `style=`
# ─────────────────────────────────────────────────────────────────────────


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

# Captura tags HTML abertas inteiras (multilinha). Não precisa cobrir tags
# fechadas, só queremos validar atributos do elemento de abertura.
_TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)([^>]*?)/?>", re.DOTALL)
_STYLE_ATTR_RE = re.compile(r'(?:^|\s)style\s*=\s*"([^"]*)"', re.DOTALL)
_ALPINE_STYLE_ATTR_RE = re.compile(
    r'(?:^|\s)(?:x-bind:style|:style)\s*=\s*"([^"]*)"', re.DOTALL
)


def _all_html_templates():
    return sorted(TEMPLATES_DIR.rglob("*.html"))


def _line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _bind_value_is_object(value: str) -> bool:
    """O valor do bind é seguro se for um objeto JS (mescla com `style=`).

    Aceitamos:
    - `{ ... }` direto
    - chamada de função (ex.: `getStyle(...)`), devolve objeto/strings;
      é raro no projeto e fica como exceção explícita.

    Rejeitamos:
    - `'...'`, `"..."`           → string literal
    - `cond ? '...' : '...'`     → ternário com strings
    - qualquer coisa que comece com aspa
    """
    stripped = value.strip()
    if not stripped:
        return False
    return stripped.startswith("{")


def _find_violations_in_template(path: Path):
    """Retorna [(linha, fragmento), ...] para tags com bug do Alpine."""
    src = path.read_text(encoding="utf-8")
    violations = []
    for m in _TAG_RE.finditer(src):
        attrs_blob = m.group(2) or ""
        if not attrs_blob:
            continue
        has_static = bool(_STYLE_ATTR_RE.search(attrs_blob))
        bind_match = _ALPINE_STYLE_ATTR_RE.search(attrs_blob)
        if not (has_static and bind_match):
            continue
        bind_value = bind_match.group(1)
        if _bind_value_is_object(bind_value):
            continue
        line = _line_of(src, m.start())
        snippet = m.group(0).strip().splitlines()[0][:140]
        violations.append((line, snippet, bind_value.strip()[:120]))
    return violations


class TestAlpineStyleBindings:
    """Garante que nenhum template re-introduz o anti-pattern do Alpine."""

    def test_helpers_de_parsing_funcionam(self):
        # Sanity check: os regex pegam o que prometem.
        assert _bind_value_is_object("{ background: 'red' }") is True
        assert _bind_value_is_object("{}") is True
        assert (
            _bind_value_is_object("connected ? 'background:green' : 'background:red'")
            is False
        )
        assert _bind_value_is_object("'background:red'") is False
        assert _bind_value_is_object('"background:red"') is False
        assert _bind_value_is_object("") is False

    def test_helper_detecta_bug_em_amostra_sintetica(self, tmp_path):
        bad = tmp_path / "bad.html"
        bad.write_text(
            '<div style="display:flex" :style="x ? \'background:red\' : \'\'"></div>',
            encoding="utf-8",
        )
        violations = _find_violations_in_template(bad)
        assert len(violations) == 1, violations

    def test_helper_aceita_objeto_em_amostra_sintetica(self, tmp_path):
        good = tmp_path / "good.html"
        good.write_text(
            '<div style="display:flex" :style="{ background: x ? \'red\' : \'\' }"></div>',
            encoding="utf-8",
        )
        assert _find_violations_in_template(good) == []

    def test_helper_aceita_bind_sem_style_estatico(self, tmp_path):
        # Se NÃO há style estático para "preservar", string no :style é ok.
        f = tmp_path / "ok.html"
        f.write_text(
            '<div :style="x ? \'color:red\' : \'\'"></div>',
            encoding="utf-8",
        )
        assert _find_violations_in_template(f) == []

    def test_nenhum_template_tem_string_em_bind_style_com_style_estatico(self):
        """Se isso falhar, troque o `:style="'...'" / x-bind:style="'...'"`
        por `:style="{ chave: ..., chave2: ... }"` no template apontado.
        Strings em `:style` substituem o `style=` estático por completo no
        Alpine, apagando `display:flex`, `padding`, `width`, etc.
        """
        problemas = []
        for tpl in _all_html_templates():
            for line, snippet, value in _find_violations_in_template(tpl):
                rel = tpl.relative_to(TEMPLATES_DIR)
                problemas.append(f"{rel}:{line} → bind={value!r} | {snippet}")
        assert not problemas, (
            "Templates com :style/x-bind:style em STRING sobrescrevendo "
            "style= estático (substitua por objeto):\n  - "
            + "\n  - ".join(problemas)
        )


# ─────────────────────────────────────────────────────────────────────────
# 2) Layout do simulador de entrevistas, `take.html`
# ─────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestInterviewTakeLayout:
    """Garante que as alternativas ficam empilhadas e cada uma é um label
    independente, evita o bug onde todas saíam numa única linha."""

    @pytest.fixture
    def attempt_em_andamento(self, db, admitted_user, client):
        from apps.interviews.models import (
            InterviewAttempt,
            InterviewQuestion,
            LEVEL_JUNIOR,
            QUESTIONS_PER_TEST,
        )

        for i in range(QUESTIONS_PER_TEST):
            InterviewQuestion.objects.create(
                level=LEVEL_JUNIOR,
                category="Linux",
                statement=(
                    "Qual a diferença entre `>` e `>>` em redirecionamento de saída?"
                ),
                choices=[
                    "São equivalentes.",
                    "Com `>`, o arquivo é sobrescrito (truncado); com `>>`, a saída acrescenta ao final.",
                    "Com `>`, a saída só acrescenta; com `>>`, o arquivo é truncado — inverte o correto.",
                    "Ambos exigem permissão root.",
                ],
                correct_index=1,
                order=i,
            )
        client.force_login(admitted_user)
        client.post(reverse("interviews:start", args=[LEVEL_JUNIOR]))
        return InterviewAttempt.objects.get(user=admitted_user)

    def _get_html(self, client, attempt):
        resp = client.get(reverse("interviews:take", args=[attempt.pk]))
        assert resp.status_code == 200
        return resp.content.decode("utf-8")

    def test_existe_um_radio_por_alternativa(
        self, client, admitted_user, attempt_em_andamento
    ):
        html = self._get_html(client, attempt_em_andamento)
        radios = re.findall(r'<input[^>]+type="radio"[^>]+name="choice"', html)
        assert len(radios) == 4, (
            f"Esperava 4 radios (um por alternativa), encontrei {len(radios)}"
        )

    def test_radios_tem_values_0_a_3(
        self, client, admitted_user, attempt_em_andamento
    ):
        html = self._get_html(client, attempt_em_andamento)
        for i in range(4):
            assert re.search(
                rf'<input[^>]+name="choice"[^>]+value="{i}"', html
            ) or re.search(
                rf'<input[^>]+value="{i}"[^>]+name="choice"', html
            ), f"radio com value={i} não encontrado"

    def test_container_de_alternativas_empilha_em_coluna(
        self, client, admitted_user, attempt_em_andamento
    ):
        """O container deve garantir empilhamento via CSS no `style=`
        estático, não pode depender só de classes Tailwind do CDN
        (que podem não chegar a tempo) nem do display:flex implícito de
        labels (que é inline)."""
        html = self._get_html(client, attempt_em_andamento)
        # padrão esperado no take.html: <div style="display:flex;flex-direction:column;...">
        m = re.search(
            r'<div\s+style="[^"]*display\s*:\s*flex[^"]*flex-direction\s*:\s*column[^"]*"',
            html,
        )
        assert m, (
            "Container das alternativas não tem `display:flex; flex-direction:column` "
            "no style estático, risco de voltarem a renderizar lado a lado."
        )

    def test_cada_label_de_alternativa_tem_display_flex_e_largura_total(
        self, client, admitted_user, attempt_em_andamento
    ):
        """Cada `<label>` de alternativa deve ter `display:flex` e `width:100%`
        no style estático para ocupar a linha inteira (evita inline default)."""
        html = self._get_html(client, attempt_em_andamento)
        labels = re.findall(r"<label\b[^>]*>", html, flags=re.DOTALL)
        # filtra só os que envolvem o radio (descartando outros labels da página)
        labels_choice = [
            tag
            for tag in labels
            if re.search(r"forloop|x-bind:style|:style|x-model|choice", tag)
        ]
        assert labels_choice, "Nenhum <label> de alternativa encontrado"
        for tag in labels_choice:
            assert "display:flex" in tag, f"label sem display:flex: {tag[:160]}"
            assert "width:100%" in tag, f"label sem width:100%: {tag[:160]}"

    def test_label_de_alternativa_usa_objeto_em_xbind_style(
        self, client, admitted_user, attempt_em_andamento
    ):
        """Regressão direta do bug original: o `x-bind:style` precisa ser
        um objeto JS, nunca uma string ternária."""
        html = self._get_html(client, attempt_em_andamento)
        labels = re.findall(r"<label\b[^>]*>", html, flags=re.DOTALL)
        labels_with_bind = [
            t for t in labels if re.search(r"(?:x-bind:style|:style)\s*=", t)
        ]
        assert labels_with_bind, "Esperava labels com bind do Alpine"
        for tag in labels_with_bind:
            m = re.search(r'(?:x-bind:style|:style)\s*=\s*"([^"]*)"', tag, re.DOTALL)
            assert m, tag
            value = m.group(1).strip()
            assert value.startswith("{"), (
                "x-bind:style do label deve ser um OBJETO `{ ... }`. "
                f"Hoje está: {value[:120]!r}"
            )
