"""Testes do app courses: modelos, quiz, integridade dos dados de seed."""
from __future__ import annotations

import re

import pytest
from django.urls import reverse
from django.utils import translation

from apps.courses.models import Choice, Lab, Lesson, Phase, Question, Topic
from apps.courses.seed_data import PHASES
from apps.courses.seed_data.labs import LABS
from apps.gamification.models import LabCompletion, TopicAttempt, TopicScore

ALL_TOPIC_TITLES = {t["title"] for phase in PHASES for t in phase["topics"]}


@pytest.mark.django_db
class TestPhaseAndTopicModels:
    def test_phase_str_e_slug_automatico(self):
        phase = Phase.objects.create(name="Fase X", order=42)
        assert "Fase 42" in str(phase)
        assert phase.slug == "fase-x"

    def test_topic_slug_automatico_e_get_absolute_url(self):
        phase = Phase.objects.create(name="Fase Y", order=2)
        topic = Topic.objects.create(phase=phase, title="Hardening Linux", order=1)
        assert topic.slug == "hardening-linux"
        assert topic.get_absolute_url() == reverse(
            "courses:topic_detail", args=["hardening-linux"]
        )

    def test_topic_unique_phase_order(self):
        from django.db import IntegrityError, transaction

        phase = Phase.objects.create(name="Fase Z", order=3)
        Topic.objects.create(phase=phase, title="A", order=1)
        with pytest.raises(IntegrityError), transaction.atomic():
            Topic.objects.create(phase=phase, title="B", order=1)


@pytest.mark.django_db
class TestBilingualDisplayFields:
    """`display_*` cai pro português até o campo `*_en` ser preenchido, e só
    troca pro inglês quando o idioma ativo é 'en' E a tradução já existe."""

    def test_topic_display_title_cai_pro_portugues_sem_traducao(self):
        phase = Phase.objects.create(name="Fase Bi", order=10)
        topic = Topic.objects.create(phase=phase, title="Hardening", order=1)
        with translation.override("en"):
            assert topic.display_title == "Hardening"

    def test_topic_display_title_usa_ingles_quando_disponivel(self):
        phase = Phase.objects.create(name="Fase Bi2", order=11)
        topic = Topic.objects.create(
            phase=phase, title="Hardening", title_en="Hardening", order=1
        )
        topic.summary = "Resumo em pt"
        topic.summary_en = "Summary in en"
        topic.save()
        with translation.override("pt-br"):
            assert topic.display_summary == "Resumo em pt"
        with translation.override("en"):
            assert topic.display_summary == "Summary in en"

    def test_lesson_display_fields(self):
        phase = Phase.objects.create(name="Fase Bi3", order=12)
        topic = Topic.objects.create(phase=phase, title="T", order=1)
        lesson = Lesson.objects.create(
            topic=topic, body="corpo pt", body_en="body en"
        )
        with translation.override("en"):
            assert lesson.display_body == "body en"
        with translation.override("pt-br"):
            assert lesson.display_body == "corpo pt"

    def test_lab_display_spec_troca_json_inteiro(self):
        phase = Phase.objects.create(name="Fase Bi4", order=13)
        topic = Topic.objects.create(phase=phase, title="T2", order=1)
        lab = Lab.objects.create(
            topic=topic,
            kind="terminal",
            title="Lab",
            spec={"scenario": "pt"},
            spec_en={"scenario": "en"},
        )
        with translation.override("en"):
            assert lab.display_spec == {"scenario": "en"}
        with translation.override("pt-br"):
            assert lab.display_spec == {"scenario": "pt"}

    def test_lab_display_spec_sem_traducao_cai_pro_original(self):
        phase = Phase.objects.create(name="Fase Bi5", order=14)
        topic = Topic.objects.create(phase=phase, title="T3", order=1)
        lab = Lab.objects.create(
            topic=topic, kind="terminal", title="Lab", spec={"scenario": "pt"}
        )
        with translation.override("en"):
            assert lab.display_spec == {"scenario": "pt"}


@pytest.mark.django_db
class TestLanguageSwitcher:
    def test_set_language_view_alterna_idioma(self, client):
        resp = client.post(
            reverse("set_language"),
            {"language": "en", "next": "/"},
        )
        assert resp.status_code == 302
        assert client.cookies["django_language"].value == "en"

    def test_set_language_preserva_querystring_do_next(self, client):
        resp = client.post(
            reverse("set_language"),
            {"language": "en", "next": "/trilha/topico/fundamentos-de-linux/?p=3"},
        )
        assert resp.status_code == 302
        assert resp["Location"].endswith("/trilha/topico/fundamentos-de-linux/?p=3")

    def test_lang_switch_inclui_querystring_no_next(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        url = reverse("courses:topic_detail", args=[seed_phases["topic"].slug])
        resp = client.get(f"{url}?p=3")
        assert resp.status_code == 200
        assert f'name="next" value="{url}?p=3"'.encode() in resp.content

    def test_trocar_idioma_volta_para_a_mesma_pagina_da_aula(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        url = reverse("courses:topic_detail", args=[seed_phases["topic"].slug])
        next_url = f"{url}?p=3"
        resp = client.post(reverse("set_language"), {"language": "en", "next": next_url})
        assert resp.status_code == 302
        assert resp["Location"] == next_url
        landed = client.get(resp["Location"])
        assert landed.status_code == 200
        assert f'name="next" value="{next_url}"'.encode() in landed.content


class TestSeedDataIntegrity:
    """Garante que o conteúdo das 6 fases está bem-formado."""

    def test_existem_6_fases(self):
        assert len(PHASES) == 6

    def test_cada_fase_tem_10_topicos(self):
        for i, phase in enumerate(PHASES, start=1):
            assert len(phase["topics"]) == 10, (
                f"Fase {i} tem {len(phase['topics'])} tópicos (esperava 10)"
            )

    def test_cada_topico_tem_no_minimo_5_materiais(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                materials = topic.get("materials", [])
                assert len(materials) >= 5, (
                    f"{topic['title']} tem só {len(materials)} materiais"
                )

    def test_cada_topico_tem_10_questoes_com_unica_correta(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                questions = topic.get("questions", [])
                assert len(questions) == 10, (
                    f"{topic['title']} tem {len(questions)} questões (esperava 10)"
                )
                for qi, q in enumerate(questions):
                    correct = [c for c in q["choices"] if c.get("correct")]
                    assert len(correct) == 1, (
                        f"{topic['title']} Q{qi}: deve ter exatamente 1 alternativa correta"
                    )

    def test_alternativas_nao_estao_sempre_na_primeira_posicao(self):
        """A correta não pode ser sempre índice 0, exige embaralhamento."""
        first_position_count = 0
        total = 0
        for phase in PHASES:
            for topic in phase["topics"]:
                for q in topic.get("questions", []):
                    total += 1
                    if q["choices"][0].get("correct"):
                        first_position_count += 1
        # Com 500 questões embaralhadas, a taxa na posição 0 deve ser ~25%
        # (1 em 4). Aceitamos até 40%, se passar disso o shuffle não está
        # funcionando. Na prática fica em torno de 25%.
        ratio = first_position_count / total
        assert ratio < 0.40, (
            f"Alternativa correta está na posição 0 em {ratio:.0%} das questões; "
            f"o embaralhamento não está funcionando."
        )

    def test_lessons_tem_intro_body_e_practical_preenchidos(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                lesson = topic.get("lesson", {})
                for key in ("intro", "body", "practical"):
                    assert lesson.get(key), (
                        f"{topic['title']} sem '{key}' na aula"
                    )

    def test_titulos_de_topico_sao_unicos(self):
        seen = set()
        for phase in PHASES:
            for topic in phase["topics"]:
                assert topic["title"] not in seen, f"Tópico duplicado: {topic['title']}"
                seen.add(topic["title"])
        assert len(seen) == 60


_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_HEADING_NUM_RE = re.compile(r"^\s*(\d{1,2})\s*[.)]")
# "seção 7", "seções 4 e 5", "section 7", "sections 4 and 5". O grupo repetido
# só casa quando vem outro NÚMERO depois da conjunção, então "seção 5, e o
# resto da frase" não é confundido com uma lista.
_REF_RES = (
    re.compile(r"\bseç(?:ão|ões)\s+(\d{1,2}(?:\s*(?:,|e)\s*\d{1,2})*)", re.IGNORECASE),
    re.compile(r"\bsections?\s+(\d{1,2}(?:\s*(?:,|and)\s*\d{1,2})*)", re.IGNORECASE),
)


def _section_numbers(body: str) -> set[int]:
    """Números dos `<h3>` da aula. Todos os 60 tópicos usam 'N. Título'."""
    out: set[int] = set()
    for raw in _H3_RE.findall(body or ""):
        m = _HEADING_NUM_RE.match(_TAG_RE.sub("", raw).strip())
        if m:
            out.add(int(m.group(1)))
    return out


def _referenced_sections(html: str) -> list[int]:
    out: list[int] = []
    text = _TAG_RE.sub(" ", html or "")
    for regex in _REF_RES:
        for m in regex.finditer(text):
            out.extend(int(n) for n in re.findall(r"\d{1,2}", m.group(1)))
    return out


class TestReferenciasDeSecaoNoExercicio:
    """O exercício prático cita seções da aula por número; elas precisam existir.

    Os exercícios mandam o aluno voltar a um ponto específico ("é a armadilha
    da seção 6"), e é isso que liga a prática à leitura. A referência é
    posicional: inserir ou reordenar um `<h3>` desloca a numeração e faz o
    exercício apontar para o assunto errado — sem quebrar nada e sem aviso,
    que é o pior tipo de erro de conteúdo.
    """

    def test_toda_secao_citada_existe_na_aula(self):
        for phase in PHASES:
            for topic in phase["topics"]:
                lesson = topic["lesson"]
                for practical_key, body_key in (
                    ("practical", "body"),
                    ("practical_en", "body_en"),
                ):
                    existing = _section_numbers(lesson.get(body_key) or "")
                    if not existing:
                        continue
                    for cited in _referenced_sections(lesson.get(practical_key) or ""):
                        assert cited in existing, (
                            f"{topic['title']} [{practical_key}]: cita a seção "
                            f"{cited}, mas a aula vai de {min(existing)} a "
                            f"{max(existing)}"
                        )

    def test_h3_continuam_numerados(self):
        """A checagem acima depende disso; sem número, ela passaria vazia."""
        for phase in PHASES:
            for topic in phase["topics"]:
                for body_key in ("body", "body_en"):
                    body = topic["lesson"].get(body_key) or ""
                    headings = [_TAG_RE.sub("", h).strip() for h in _H3_RE.findall(body)]
                    for heading in headings:
                        assert _HEADING_NUM_RE.match(heading), (
                            f"{topic['title']} [{body_key}]: heading sem número "
                            f"({heading[:40]!r}) — as citações do exercício "
                            "prático deixam de ser verificáveis"
                        )

    def test_a_checagem_nao_passa_vazia(self):
        """Rede de segurança: se a convenção sumir, o teste acima vira decoração."""
        total = sum(
            len(_referenced_sections(topic["lesson"].get(key) or ""))
            for phase in PHASES
            for topic in phase["topics"]
            for key in ("practical", "practical_en")
        )
        assert total > 100, (
            f"só {total} referências a seção encontradas nos 120 exercícios; "
            "ou a convenção mudou, ou o regex parou de casar"
        )


class TestLabDataIntegrity:
    """Garante que os 60 laboratórios (1 por tópico) estão bem-formados.

    Cobre a queixa "não tem laboratório prático de verdade": cada um dos 60
    tópicos precisa ter exatamente 1 lab, com `topic_title` batendo com um
    tópico real (senão `seed_labs` levanta CommandError silenciosamente
    ignorável em produção) e `spec` no formato que `kind` espera.
    """

    def test_existem_60_labs_um_por_topico(self):
        assert len(LABS) == 60

    def test_topic_title_bate_com_topico_real(self):
        for lab in LABS:
            assert lab["topic_title"] in ALL_TOPIC_TITLES, (
                f"Lab {lab['title']!r} aponta pro tópico "
                f"{lab['topic_title']!r}, que não existe em seed_data"
            )

    def test_cada_topico_tem_exatamente_1_lab(self):
        titles = [lab["topic_title"] for lab in LABS]
        assert len(titles) == len(set(titles)) == 60

    def test_kind_e_um_dos_validos(self):
        validos = {k for k, _ in Lab.Kind.choices}
        for lab in LABS:
            assert lab["kind"] in validos, f"{lab['title']}: kind {lab['kind']!r} inválido"

    def test_spec_terminal_tem_pool_sem_token_duplicado(self):
        for lab in LABS:
            if lab["kind"] != "terminal":
                continue
            spec = lab["spec"]
            pool = spec["correct_command"] + spec["distractor_tokens"]
            assert len(set(pool)) == len(pool), f"{lab['title']}: token duplicado no pool"

    def test_accepted_commands_sao_o_mesmo_conjunto_de_tokens(self):
        for lab in LABS:
            if lab["kind"] != "terminal":
                continue
            for key in ("spec", "spec_en"):
                spec = lab.get(key) or {}
                if "accepted_commands" not in spec:
                    continue
                canon = spec["correct_command"]
                for alt in spec["accepted_commands"]:
                    assert sorted(alt) == sorted(canon), (
                        f"{lab['title']} {key}: {alt} ≠ tokens de {canon}"
                    )
                    assert alt != canon, f"{lab['title']} {key}: accepted duplica o gabarito"

    def test_ordens_de_flag_equivalentes_passam_e_as_invalidas_nao(self):
        from apps.courses.command_equiv import commands_equivalent

        iguais = [
            (["dig", "+short", "exemplo.com"], ["dig", "exemplo.com", "+short"]),
            (["journalctl", "-p", "err", "-S", "today"], ["journalctl", "-S", "today", "-p", "err"]),
            (["syft", "imagem:tag", "-o", "cyclonedx-json"], ["syft", "-o", "cyclonedx-json", "imagem:tag"]),
            (["kubectl", "get", "pods", "-n", "default"], ["kubectl", "-n", "default", "get", "pods"]),
            (["kubectl", "get", "pods", "-n", "default"], ["kubectl", "get", "-n", "default", "pods"]),
            (["docker", "run", "-d", "--name", "web", "nginx"], ["docker", "run", "--name", "web", "-d", "nginx"]),
            (["find", "/", "-perm", "-4000", "-type", "f"], ["find", "/", "-type", "f", "-perm", "-4000"]),
            (["trivy", "image", "--severity", "CRITICAL", "--exit-code", "1", "myapp:dev"],
             ["trivy", "image", "--exit-code", "1", "--severity", "CRITICAL", "myapp:dev"]),
        ]
        diferentes = [
            (["sudo", "sshd", "-t"], ["sudo", "-t", "sshd"]),
            (["git", "rm", "--cached"], ["git", "--cached", "rm"]),
            (["pre-commit", "run", "--all-files"], ["pre-commit", "--all-files", "run"]),
            (["git", "checkout", "-b", "feature"], ["git", "checkout", "feature", "-b"]),
            (["ssh-keygen", "-t", "ed25519"], ["ssh-keygen", "ed25519", "-t"]),
            (["setfacl", "-m", "u:visitante:r--", "config.yml"], ["setfacl", "-m", "config.yml", "u:visitante:r--"]),
            (["docker", "run", "-d", "--name", "web", "nginx"], ["docker", "run", "-d", "nginx", "--name", "web"]),
            (["ps", "-eo", "pid,uid,user,cmd", "|", "head"], ["ps", "pid,uid,user,cmd", "|", "head", "-eo"]),
            (["journalctl", "-p", "err", "-S", "today"], ["journalctl", "err", "-S", "today", "-p"]),
        ]
        for left, right in iguais:
            assert commands_equivalent(left, right), (left, right)
        for left, right in diferentes:
            assert not commands_equivalent(left, right), (left, right)

    def test_accepted_commands_autorais_sao_o_mesmo_comando(self):
        from apps.courses.command_equiv import commands_equivalent

        for lab in LABS:
            if lab["kind"] != "terminal":
                continue
            for key in ("spec", "spec_en"):
                spec = lab.get(key) or {}
                for alt in spec.get("accepted_commands") or []:
                    assert commands_equivalent(spec["correct_command"], alt), (
                        f"{lab['title']} {key}: {alt} não é o mesmo comando"
                    )

    def test_spec_find_flaw_indice_dentro_do_range(self):
        for lab in LABS:
            if lab["kind"] != "find_flaw":
                continue
            spec = lab["spec"]
            assert 0 <= spec["flaw_line_index"] < len(spec["lines"]), lab["title"]

    def test_spec_order_mesmos_itens_embaralhados_e_ordenados(self):
        for lab in LABS:
            if lab["kind"] != "order":
                continue
            spec = lab["spec"]
            assert sorted(spec["steps_shuffled"]) == sorted(spec["correct_order"]), lab["title"]

    def test_spec_blanks_marcador_aparece_no_template(self):
        for lab in LABS:
            if lab["kind"] != "blanks":
                continue
            spec = lab["spec"]
            for key, blank in spec["blanks"].items():
                assert f"___{key}___" in spec["template"], f"{lab['title']}: falta marcador {key}"
                assert blank["correct"] in blank["options"], lab["title"]

    def test_spec_scenario_tem_exatamente_1_choice_boa(self):
        for lab in LABS:
            if lab["kind"] != "scenario":
                continue
            spec = lab["spec"]
            boas = sum(1 for c in spec["choices"] if c["good"])
            assert boas == 1, f"{lab['title']}: {boas} choices boas (esperava 1)"

    def test_expand_labs_um_por_pagina_de_cada_topico(self):
        from apps.core.pagination import paginate_html_sections
        from apps.courses.seed_data import PHASES
        from apps.courses.seed_data.page_labs import expand_labs

        expanded = expand_labs()
        by_topic: dict[str, list[int]] = {}
        for lab in expanded:
            by_topic.setdefault(lab["topic_title"], []).append(lab["lesson_page"])
            assert lab["lesson_page"] >= 1
            assert lab["kind"] in {k for k, _ in Lab.Kind.choices}

        assert len(by_topic) == 60
        for phase in PHASES:
            for topic in phase["topics"]:
                body = (topic.get("lesson") or {}).get("body") or ""
                n = len(paginate_html_sections(body) or [body])
                pages = sorted(by_topic[topic["title"]])
                # Página sem material concreto fica SEM lab de propósito (ver
                # docstring de expand_labs): exercício de fachada, cuja
                # resposta saía por eliminação, era pior que nenhum. O que
                # continua valendo: no máximo 1 lab por página, sem repetir
                # página, e todo tópico com pelo menos um lab.
                assert pages == sorted(set(pages)), topic["title"]
                assert pages, topic["title"]
                assert max(pages) <= n, topic["title"]

    def test_labs_gerados_sao_praticos_nao_quiz_de_tema(self):
        from apps.courses.seed_data.labs import LABS
        from apps.courses.seed_data.page_labs import expand_labs

        authored_titles = {lab["title"] for lab in LABS}
        kinds = {"terminal": 0, "order": 0, "find_flaw": 0, "blanks": 0, "scenario": 0}
        for lab in expand_labs():
            kinds[lab["kind"]] = kinds.get(lab["kind"], 0) + 1
            if lab["title"] in authored_titles:
                continue
            spec = lab["spec"]
            if lab["kind"] == "scenario":
                sit = spec.get("situation", "")
                assert "tema central" not in sit.lower()
                assert "central topic" not in sit.lower()
                assert "termo que entra primeiro" not in sit.lower()
                assert "escrevendo o runbook" not in sit.lower()
                assert "você controla" not in sit.lower()
                boas = sum(1 for c in spec["choices"] if c["good"])
                assert boas == 1, lab["title"]
            assert "Complete o runbook" not in lab["title"]
            if lab["kind"] == "blanks":
                assert "termo que entra primeiro" not in spec.get("template", "")
            if lab["kind"] == "terminal":
                pool = spec["correct_command"] + spec["distractor_tokens"]
                assert len(set(pool)) == len(pool), lab["title"]
                cmd = " ".join(spec["correct_command"])
                sit = spec.get("scenario", "")
                assert cmd not in sit, f"{lab['title']}: enunciado entrega `{cmd}`"
                for tok in spec["correct_command"]:
                    if len(tok) >= 4 and tok.startswith(("-", "+", "/")):
                        continue
                    if len(tok) >= 5:
                        assert tok not in sit, f"{lab['title']}: enunciado vaza `{tok}`"
            if lab["kind"] == "order":
                assert sorted(spec["steps_shuffled"]) == sorted(spec["correct_order"])
            if lab["kind"] == "find_flaw":
                assert 0 <= spec["flaw_line_index"] < len(spec["lines"])
                gabarito = spec["lines"][spec["flaw_line_index"]]
                assert "\n" not in gabarito, lab["title"]
                assert len(gabarito) <= 78, lab["title"]
            if lab["kind"] == "blanks":
                for key, blank in spec["blanks"].items():
                    assert f"___{key}___" in spec["template"]
                    assert blank["correct"] in blank["options"]
        practical = kinds["terminal"] + kinds["order"] + kinds["find_flaw"] + kinds["blanks"]
        assert kinds["terminal"] >= 40, kinds
        assert practical >= 100, kinds
        generic = sum(
            1
            for lab in expand_labs()
            if lab["title"] not in authored_titles
            and lab["kind"] == "scenario"
            and "menor privilégio possível" in lab["spec"]["choices"][0]["text"]
        )
        assert generic == 0, generic

    def test_labs_gerados_nao_usam_distrator_caricato(self):
        """Distrator absurdo entrega a resposta por eliminação.

        "Abrir 0.0.0.0 e chmod 777 'só para testar'" aparecia em 135 dos 361
        labs, inclusive em seções onde nem fazia sentido (região AWS, cultura
        DevSecOps): o aluno descartava sem ler e o exercício virava 2 opções.
        """
        from apps.courses.seed_data.labs import LABS
        from apps.courses.seed_data.page_labs import expand_labs

        authored_titles = {lab["title"] for lab in LABS}
        for lab in expand_labs():
            if lab["title"] in authored_titles:
                continue
            for spec_key in ("spec", "spec_en"):
                for choice in (lab.get(spec_key) or {}).get("choices", []):
                    text = choice["text"].lower()
                    assert "chmod 777" not in text, f"{lab['title']}: {choice['text']}"
                    assert "ignorar a tabela" not in text, lab["title"]
                    assert "ignore the table" not in text, lab["title"]

    def test_order_so_para_lista_realmente_sequencial(self):
        """Ordenar só faz sentido quando existe uma ordem certa.

        Antes, qualquer `<li>` da página virava "ordene as etapas" e o
        gabarito era a ordem do HTML — arbitrária para lista de ferramentas
        (ELK/Loki/Datadog), ameaças ou itens de checklist.
        """
        from apps.courses.seed_data.page_labs import (
            _CHECKLIST_HEADING_RE,
            _looks_sequential,
            expand_labs,
        )
        from apps.courses.seed_data.labs import LABS

        authored_titles = {lab["title"] for lab in LABS}
        for lab in expand_labs():
            if lab["kind"] != "order" or lab["title"] in authored_titles:
                continue
            # O título é truncado para caber na UI, então não dá para
            # reconstruir o heading original a partir dele: validamos as
            # propriedades observáveis do exercício.
            assert not _CHECKLIST_HEADING_RE.search(lab["title"]), lab["title"]
            steps = lab["spec"]["correct_order"]
            assert len(steps) == len(set(steps)), lab["title"]
            perguntas = sum(1 for s in steps if s.rstrip().endswith("?"))
            assert perguntas < 2, f"{lab['title']}: lista de verificações, não etapas"

    def test_lab_autoral_nao_cai_antes_da_aula_ensinar_o_comando(self):
        """O exercício não pode chegar antes do conteúdo que o resolve.

        O lab de `setfacl` caía na página 2 de "Fundamentos de Linux", mas
        `setfacl` só é apresentado na página 3 — o aluno via um comando que
        a aula ainda não tinha ensinado e não tinha como responder.
        """
        from apps.courses.seed_data import PHASES
        from apps.courses.seed_data.labs import LABS
        from apps.courses.seed_data.page_labs import _topic_pages, assign_authored_page

        authored = {lab["topic_title"]: lab for lab in LABS}
        for phase in PHASES:
            for topic in phase["topics"]:
                lab = authored.get(topic["title"])
                if not lab or lab["kind"] != "terminal":
                    continue
                command = (lab["spec"].get("correct_command") or [None])[0]
                pages, _ = _topic_pages(topic)
                if not command or not any(command.lower() in p.lower() for p in pages):
                    continue
                page = pages[assign_authored_page(pages, lab) - 1]
                assert command.lower() in page.lower(), (
                    f"{topic['title']}: lab pede `{command}` numa página que "
                    "não apresenta o comando"
                )

    def test_looks_sequential_rejeita_lista_sem_ordem(self):
        from apps.courses.seed_data.page_labs import _looks_sequential

        ferramentas = [
            "Elastic Stack (ELK): indexa tudo full-text. Caro em armazenamento.",
            "Grafana Loki: indexa só labels. Storage barato (S3).",
            "CloudWatch Logs: gerenciado, ótimo para começar.",
        ]
        assert not _looks_sequential("Onde centralizar logs", ferramentas)
        assert not _looks_sequential("Checklist mensal", ferramentas)

        verificacoes = [
            "Conta root tem MFA hardware?",
            "CloudTrail está ativo em todas as regiões?",
            "Block Public Access está ativado na conta inteira?",
        ]
        assert not _looks_sequential("Revisão de conta", verificacoes)

        etapas = [
            "1. Gerar o par de chaves na máquina do desenvolvedor.",
            "2. Enviar a chave pública para o servidor.",
            "3. Desabilitar a autenticação por senha no sshd.",
        ]
        assert _looks_sequential("Configurando acesso", etapas)
        assert _looks_sequential("Fluxo de deploy", etapas)


@pytest.mark.django_db
class TestLabNaPaginaCerta:
    """A página renderizada precisa ser a mesma que gerou o lab.

    `expand_labs` calcula o `lesson_page` de cada lab paginando o corpo CRU
    da aula, mas a página exibida passa antes pelo glossário e, em inglês,
    por outro texto. Enquanto esses três caminhos paginavam por conta
    própria, a seção que caía na página N era diferente em cada um — o aluno
    abria a página sobre mirror interno e encontrava um exercício sobre
    typosquatting, assunto da seção seguinte, que ele ainda não tinha lido.
    """

    def setup_method(self):
        from django.core.cache import cache

        cache.clear()

    def _h3_por_pagina(self, pages) -> list[int]:
        return [str(page).count("<h3") for page in pages]

    def test_glossario_nao_desloca_a_secao_para_outra_pagina(self):
        from django.core.management import call_command

        from apps.core.pagination import paginate_html_sections
        from apps.core.templatetags.pdt_extras import paginate_lesson_body

        call_command("seed_glossary", verbosity=0)
        for phase in PHASES:
            for topic in phase["topics"]:
                body = (topic.get("lesson") or {}).get("body") or ""
                if not body:
                    continue
                seed = paginate_html_sections(body) or [body]
                render = paginate_lesson_body(body, body)
                assert self._h3_por_pagina(render) == [p.count("<h3") for p in seed], (
                    f"{topic['title']}: aluno vê {len(render)} páginas, "
                    f"seed calculou lab para {len(seed)}"
                )

    def test_ingles_corta_nas_mesmas_secoes_que_o_portugues(self):
        from django.core.management import call_command

        from apps.core.pagination import paginate_html_sections
        from apps.core.templatetags.pdt_extras import paginate_lesson_body

        call_command("seed_glossary", verbosity=0)
        for phase in PHASES:
            for topic in phase["topics"]:
                lesson = topic.get("lesson") or {}
                body, body_en = lesson.get("body") or "", lesson.get("body_en") or ""
                if not body or not body_en:
                    continue
                seed = paginate_html_sections(body) or [body]
                render_en = paginate_lesson_body(body_en, body)
                assert self._h3_por_pagina(render_en) == [p.count("<h3") for p in seed], (
                    f"{topic['title']}: em inglês a seção cai em outra página"
                )


@pytest.mark.django_db
class TestSeedLabsCommand:
    """Mesmo padrão de TestSeedTopicsCommand: idempotente, preserva edição."""

    def test_seed_labs_cria_um_por_topico(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        from apps.courses.seed_data.page_labs import expand_labs

        assert Lab.objects.count() == len(expand_labs())
        assert Topic.objects.filter(labs__isnull=True).count() == 0
        assert Lab.objects.filter(is_active=True).count() == Lab.objects.count()

    def test_seed_labs_idempotente(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        primeiro_count = Lab.objects.count()
        call_command("seed_labs", verbosity=0)
        assert Lab.objects.count() == primeiro_count

    def test_seed_labs_preserva_edicao_do_admin(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        lab = Lab.objects.first()
        lab.title = "Editado pelo mantenedor"
        lab.seed_managed = False
        lab.save(update_fields=["title", "seed_managed"])

        call_command("seed_labs", verbosity=0)
        lab.refresh_from_db()
        assert lab.title == "Editado pelo mantenedor"

    def test_seed_labs_force_sobrescreve_edicao(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        call_command("seed_labs", verbosity=0)
        lab = Lab.objects.first()
        titulo_original = lab.title
        lab.title = "Será revertido"
        lab.seed_managed = False
        lab.save(update_fields=["title", "seed_managed"])

        call_command("seed_labs", force=True, verbosity=0)
        lab.refresh_from_db()
        assert lab.title == titulo_original
        assert lab.seed_managed is True


@pytest.mark.django_db
class TestLabCompleteView:
    def test_completar_lab_soma_bonus_e_e_idempotente(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        lab = Lab.objects.create(topic=topic, kind="terminal", title="L", spec={})

        url = reverse("courses:lab_complete", args=[lab.id])
        resp = client.post(url)
        assert resp.status_code == 200
        assert resp.json()["lab_bonus"] == 1
        assert LabCompletion.objects.filter(user=admitted_user, lab=lab).count() == 1

        resp2 = client.post(url)  # refazer não deve dobrar o bônus
        assert resp2.json()["lab_bonus"] == 1
        assert LabCompletion.objects.filter(user=admitted_user, lab=lab).count() == 1

    def test_completar_lab_exige_login(self, client, seed_phases):
        topic = seed_phases["topic"]
        lab = Lab.objects.create(topic=topic, kind="terminal", title="L", spec={})
        resp = client.post(reverse("courses:lab_complete", args=[lab.id]))
        assert resp.status_code in (302, 401, 403)

    def test_lab_inativo_nao_pode_ser_completado(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        lab = Lab.objects.create(
            topic=topic, kind="terminal", title="L", spec={}, is_active=False
        )
        resp = client.post(reverse("courses:lab_complete", args=[lab.id]))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSeedTopicsCommand:
    """Verifica que o management command importa o conteúdo corretamente."""

    def test_seed_topics_cria_tudo(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        assert Phase.objects.count() == 6
        assert Topic.objects.count() == 60
        assert Question.objects.count() == 600  # 60 tópicos × 10 perguntas
        for question in Question.objects.all():
            assert question.choices.filter(is_correct=True).count() == 1

    def test_seed_topics_idempotente(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        primeiro_count = Topic.objects.count()
        call_command("seed_topics", verbosity=0)
        assert Topic.objects.count() == primeiro_count

    def test_seed_topics_preserva_aula_editada_pelo_admin(self):
        """O defeito original: o seed rodava no boot do container e apagava
        qualquer edição feita pelo admin todo dia. `seed_managed=False`
        (setado automaticamente ao salvar pelo admin, ver apps.courses.admin)
        faz o próximo `seed_topics` pular esse registro."""
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        lesson = Lesson.objects.first()
        lesson.body = "<p>Texto editado manualmente pelo mantenedor.</p>"
        lesson.seed_managed = False
        lesson.save(update_fields=["body", "seed_managed"])

        call_command("seed_topics", verbosity=0)
        lesson.refresh_from_db()
        assert lesson.body == "<p>Texto editado manualmente pelo mantenedor.</p>"

    def test_seed_topics_force_sobrescreve_edicao(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        lesson = Lesson.objects.first()
        body_original = lesson.body
        lesson.body = "<p>Editado, mas será revertido por --force.</p>"
        lesson.seed_managed = False
        lesson.save(update_fields=["body", "seed_managed"])

        call_command("seed_topics", force=True, verbosity=0)
        lesson.refresh_from_db()
        assert lesson.body == body_original
        assert lesson.seed_managed is True

    def test_seed_topics_preserva_questao_e_suas_alternativas_editadas(self):
        from django.core.management import call_command

        call_command("seed_topics", verbosity=0)
        question = Question.objects.first()
        choice_ids_antes = set(question.choices.values_list("id", flat=True))
        question.statement = "Enunciado corrigido pelo mantenedor."
        question.seed_managed = False
        question.save(update_fields=["statement", "seed_managed"])

        call_command("seed_topics", verbosity=0)
        question.refresh_from_db()
        assert question.statement == "Enunciado corrigido pelo mantenedor."
        # As Choice não foram apagadas/recriadas: mesmos IDs de antes.
        assert set(question.choices.values_list("id", flat=True)) == choice_ids_antes


@pytest.mark.django_db
class TestQuizFlow:
    """Fluxo completo do quiz: GET → POST com respostas → result + score."""

    def test_quiz_renderiza_para_admitido(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        url = reverse("courses:quiz", args=[seed_phases["topic"].slug])
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"Pergunta 0" in resp.content

    def test_quiz_acerto_total_atualiza_topic_score(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {}
        for q in seed_phases["questions"]:
            correct = q.choices.get(is_correct=True)
            post_data[f"q_{q.id}"] = correct.id

        resp = client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        assert resp.status_code == 302

        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 10
        assert attempt.finished_at is not None

        score = TopicScore.objects.get(user=admitted_user, topic=topic)
        assert score.best_quiz_score == 10
        assert score.points == 10

    def test_quiz_acerto_parcial(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {}
        for i, q in enumerate(seed_phases["questions"]):
            if i < 7:
                ch = q.choices.get(is_correct=True)
            else:
                ch = q.choices.get(is_correct=False)
            post_data[f"q_{q.id}"] = ch.id

        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 7

    def test_quiz_resposta_em_branco(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        client.post(reverse("courses:quiz", args=[topic.slug]), {})
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)
        assert attempt.score == 0

    def test_quiz_so_atualiza_best_score_se_for_maior(
        self, client, admitted_user, seed_phases
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]

        # Tentativa 1: 10/10
        post_data_perfeito = {
            f"q_{q.id}": q.choices.get(is_correct=True).id
            for q in seed_phases["questions"]
        }
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data_perfeito)

        # Tentativa 2: pior (3/10)
        post_data_ruim = {}
        for i, q in enumerate(seed_phases["questions"]):
            ch = q.choices.get(is_correct=True if i < 3 else False)
            post_data_ruim[f"q_{q.id}"] = ch.id
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data_ruim)

        score = TopicScore.objects.get(user=admitted_user, topic=topic)
        assert score.best_quiz_score == 10  # mantém o melhor

    def test_quiz_result_view_acessivel_apenas_para_dono(
        self, client, admitted_user, seed_phases, make_user
    ):
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        post_data = {
            f"q_{q.id}": q.choices.get(is_correct=True).id
            for q in seed_phases["questions"]
        }
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)

        outro = make_user(email="outro@x.com")
        client.force_login(outro)
        url = reverse("courses:quiz_result", args=[topic.slug, attempt.id])
        resp = client.get(url)
        assert resp.status_code == 404

    def test_resultado_sobrevive_a_alternativa_apagada_pelo_seed(
        self, client, admitted_user, seed_phases
    ):
        """Regressão: `choice` é SET_NULL. Antes do snapshot, rodar o seed
        (que apaga e recria as alternativas de uma questão) fazia o histórico
        de tentativas antigas mostrar "(em branco)" para respostas que o
        usuário de fato tinha dado — mesmo sem o usuário ter feito nada."""
        client.force_login(admitted_user)
        topic = seed_phases["topic"]
        question = seed_phases["questions"][0]
        picked = question.choices.get(is_correct=True)
        texto_respondido = picked.text

        # Responde tudo (não só a questão do teste): as outras 9 legitimamente
        # apareceriam como "(em branco)" se deixadas sem resposta, o que
        # confundiria uma checagem ingênua de substring na página inteira.
        post_data = {f"q_{question.id}": picked.id}
        for outra in seed_phases["questions"][1:]:
            post_data[f"q_{outra.id}"] = outra.choices.get(is_correct=True).id
        client.post(reverse("courses:quiz", args=[topic.slug]), post_data)
        attempt = TopicAttempt.objects.get(user=admitted_user, topic=topic)

        # Simula o que `seed_topics` faz com uma questão seed_managed=True:
        # apaga todas as Choice da questão.
        question.choices.all().delete()

        resp = client.get(reverse("courses:quiz_result", args=[topic.slug, attempt.id]))
        assert resp.status_code == 200
        assert texto_respondido.encode() in resp.content

        resposta = attempt.answers.get(question=question)
        assert resposta.choice_id is None  # a Choice foi apagada de verdade
        assert resposta.display_text == texto_respondido
        assert b"(em branco)" not in resp.content


@pytest.mark.django_db
class TestTopicViews:
    def test_track_view_lista_fases(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        resp = client.get(reverse("courses:track"))
        assert resp.status_code == 200
        assert b"Fase de Teste" in resp.content

    def test_topic_detail_view(self, client, admitted_user, seed_phases):
        client.force_login(admitted_user)
        url = reverse("courses:topic_detail", args=[seed_phases["topic"].slug])
        resp = client.get(url)
        assert resp.status_code == 200
        assert b"T\xc3\xb3pico de Teste" in resp.content

    def test_lab_fica_dentro_da_pagina_correspondente(self, client, admitted_user, seed_phases):
        topic = seed_phases["topic"]
        lesson = topic.lesson
        lesson.body = "".join(f"<h3>{i}. Seção</h3><p>{'x' * 1600}</p>" for i in range(1, 6))
        lesson.save(update_fields=["body"])
        Lab.objects.filter(topic=topic).delete()
        Lab.objects.create(
            topic=topic,
            kind="terminal",
            title="Lab só na página 2",
            spec={
                "scenario": "s",
                "correct_command": ["echo", "ok"],
                "distractor_tokens": ["no"],
                "explanation": "e",
            },
            lesson_page=2,
        )
        client.force_login(admitted_user)
        html = client.get(reverse("courses:topic_detail", args=[topic.slug])).content.decode()
        pages = html.split('class="lesson-page"')
        assert len(pages) >= 3
        assert "Lab só na página 2" not in pages[1]  # página 1
        assert "Lab só na página 2" in pages[2]  # página 2
        assert "Lab só na página 2" not in pages[3]  # página 3
        assert html.count("lab-card") == 1
