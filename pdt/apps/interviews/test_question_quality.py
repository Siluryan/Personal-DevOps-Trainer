"""Anti-regressão de qualidade das questões e distratores.

Os distratores das questões precisam ser **plausíveis**: o objetivo é que
um candidato que estudou só superficialmente seja tentado a marcá-los, e
não que sirvam como dica visual da resposta certa.

Estes testes impedem que voltem distratores preguiçosos como
"Não há motivo.", "Festa.", "Sorteio.", "Apenas marketing." ou alternativas
muito mais curtas que a correta (a diferença de tamanho é uma pista
imediata da resposta certa).

Os testes operam diretamente na fonte de dados (lista Python), portanto
não dependem de DB, migrations ou seeding.
"""
from __future__ import annotations

import re

import pytest

from apps.interviews.seed_data import ALL_INTERVIEW_QUESTIONS

# --- Heurísticas ---


# Frases curtas e genéricas que costumavam aparecer como distrator preguiçoso.
# São strings completas (sem pontuação variando) ou substrings que indicam
# resposta sem substância. Comparação case-insensitive.
LAZY_PHRASES = {
    # respostas-vazias clássicas
    "não há motivo",
    "sem motivo",
    "não há",
    "não há mitigação",
    "não é possível",
    "não existe",
    "não importa",
    "não importam",
    "sem ação",
    "sem ação possível",
    "sem critério",
    "sem nenhum cuidado",
    "sem governança",
    "sem segregação",
    "sem requisitos",
    "sem isolamento",
    "sem isolamento real",
    "sem cuidado",
    "sem auditoria",
    "sem buffer",
    "sem ttl",
    "sem plano",
    "sem diferença",
    "sem investimento em qualidade",
    "sem release notes",
    "sem orquestração",
    "sem diagnóstico",
    "sem design",
    "sem nada",
    "sem trade-off",
    "sem state machine",
    "sem desvantagens",
    "sem controles",
    "sem campainha",
    "nenhum existe",
    "ninguém usa",
    "nenhuma das anteriores",
    # respostas zoeira
    "festa",
    "festa de comemoração",
    "sorteio",
    "improvisar",
    "improvisação",
    "improvisação.",
    "trilha de fitness",
    "calculadora de custos",
    "cor do logo",
    "cor do gráfico",
    "cor das senhas",
    "decorar o código",
    "decorar código",
    "marketing for apps",
    "apenas marketing",
    "estética",
    "apenas por estética",
    "por estética",
    "por curiosidade",
    "apenas senha do líder",
    "tipo de chave ssh",
    "função do shell",
    "padrão de cabeçalho",
    "bug de dns",
    "tipo de log",
    "tipo de probe",
    "modo de logging",
    "tipo de erro do helm",
    "métrica de prometheus",
    "métrica de banco",
    "servidor de identidade",
    "função do kernel",
    "documento de marketing",
    "termo de marketing",
    "uma vpc",
    # negações totais
    "tudo é responsabilidade do provedor",
    "apenas a aplicação, nada mais",
    "nunca",
    "sempre",  # sozinho como alternativa inteira
    "esperar",
    "aceitar inconsistência sempre",
    "ignorar",
    "ignorar logs",
    "ignorar a query",
    "não logar nada",
    "não usar cache",
    "apagar logs",
    "apagar cache aleatoriamente",
    "apagar /tmp",
    "apagar a coluna",
    "trocar host imediatamente",
    "reinstalar o kernel",
    "reiniciar o serviço",
    "reiniciar e esperar",
    "reescrever em outra linguagem",
    "comprar mais hardware",
    "renomear servidores",
    "comprar mais ram",
    "subir tudo como root",
    "instalar 'vim' para debug",
    "comentar a importação",
    "comentar o run",
    "comentar a imagem",
    "hardcode no dockerfile",
    "hardcoded no código",
    "no readme",
    "em texto plano no yaml",
    "em texto plano para facilitar debug",
    "em variáveis de ambiente públicas",
    "em cookies",
    "apenas em cookies",
    "apenas dmesg",
    "apenas snapshots locais",
    "apenas backup",
    "apenas backup mensal",
    "apenas alertas no slack",
    "apenas chatops",
    "apenas iam legacy users",
    "apenas tecnologia",
    "apenas testar sintaxe",
    "apenas wiki opcional",
    "apenas qa externo",
    "apenas slides bonitos",
    "apenas perímetro",
    "apenas em desenvolvimento",
    "apenas para imagens",
    "apenas para migrações",
    "apenas para databases",
    "apenas para lambda",
    "apenas para windows",
    "apenas para evitar code review",
    "apenas para deixar tudo mais lento",
    "apenas chave do líder",
    "apenas restringe ips",
    "apenas mudar dns",
    "apenas timestamps",
    "apenas dns round robin",
    "apenas escalar horizontal",
    "apenas mais máquinas",
    "apenas mais alertas",
    "não há solução",
    "não há benefício",
    "não há vantagem",
    "não há.",
    "esperar passar despercebido",
    "esperar alguém perceber",
    "encerro o terminal e finjo que não vi",
    "ignoro o comentário",
    "reverto o pr sem responder",
    "levo para o pessoal e revido",
    "reclamar fora do trabalho",
    "pedir demissão imediatamente",
    "implementar do meu jeito sem avisar",
    "faço suposições silenciosas e mexo em produção",
    "capturas de tela do desktop pessoal",
    "texto em prosa de 50 páginas",
    "apenas comandos sem contexto",
    "confiar só em cursos pagos",
    "esperar a empresa pedir",
    "não estudar mais após formado",
    "demitir alguém",
    "reunião para apontar culpados",
    "documento confidencial sem ações",
    "festa de comemoração",
    "estimar somente em horas exatas",
    "não estimar nunca",
    "sempre estimar pelo melhor caso possível",
    "deploy direto em sexta à noite",
    "deploy diário em produção",
    "code review opcional",
    "versionamento manual de artefatos",
    "para deixar o pipeline mais bonito",
    "para gastar mais espaço em log",
    "para gastar tempo",
    "permitir mais hacks",
    "para deixar tudo mais lento",
    "para forçar tls",
    "para acelerar pull",
    "deixa testes mais incertos",
    "aumenta consumo de armazenamento e nada mais",
    "nada mais",
    "são iguais",
    "são equivalentes",
    "são idênticos",
    "são sinônimos",
    "são o mesmo",
    "são termos sinônimos",
    "são termos idênticos",
    "iguais",
    "são equivalentes em arquitetura",
}


def _normalize(text: str) -> str:
    """Normaliza para comparação: minúsculas, sem pontuação final, sem
    espaço duplicado e sem caracteres invisíveis."""
    s = text.strip().lower()
    s = s.rstrip(".!?;:,")
    s = re.sub(r"\s+", " ", s)
    return s


def _word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def _is_lazy(distractor: str) -> bool:
    norm = _normalize(distractor)
    if norm in LAZY_PHRASES:
        return True
    # Distrator começando com "Apenas" + 1 palavra (ex.: "Apenas marketing.",
    # "Apenas backup.") indica resposta vazia.
    if re.fullmatch(r"apenas \w+", norm):
        return True
    # "Sem X" com 2 palavras, ex.: "Sem buffer.", "Sem critério."
    if re.fullmatch(r"sem \w+", norm):
        return True
    return False


def _all_questions():
    out = []
    for level, questions in ALL_INTERVIEW_QUESTIONS.items():
        for i, q in enumerate(questions):
            out.append((level, i, q))
    return out


# --- Sanity das listas ---


class TestSeedListsSanity:
    """As listas de seed são consistentes ao próprio Python (não dependem de DB)."""

    def test_existem_3_niveis_com_100_questoes_cada(self):
        assert set(ALL_INTERVIEW_QUESTIONS.keys()) == {"junior", "pleno", "senior"}
        for level, qs in ALL_INTERVIEW_QUESTIONS.items():
            assert len(qs) == 100, f"{level}: {len(qs)} (esperava 100)"

    def test_estrutura_de_cada_questao(self):
        required = {"category", "statement", "choices", "correct_index", "explanation"}
        for level, idx, q in _all_questions():
            faltando = required - set(q.keys())
            assert not faltando, f"{level}#{idx} faltando keys: {faltando}"

    def test_quatro_alternativas_por_questao(self):
        for level, idx, q in _all_questions():
            assert len(q["choices"]) == 4, (
                f"{level}#{idx} tem {len(q['choices'])} choices (esperava 4)"
            )

    def test_correct_index_dentro_do_intervalo(self):
        for level, idx, q in _all_questions():
            assert 0 <= q["correct_index"] < len(q["choices"]), (
                f"{level}#{idx} correct_index inválido: {q['correct_index']}"
            )

    def test_alternativas_unicas_por_questao(self):
        for level, idx, q in _all_questions():
            normalized = [_normalize(c) for c in q["choices"]]
            assert len(set(normalized)) == 4, (
                f"{level}#{idx} tem alternativas duplicadas: {q['choices']}"
            )

    def test_explanation_nao_vazia(self):
        for level, idx, q in _all_questions():
            assert q["explanation"].strip(), (
                f"{level}#{idx} sem explicação: {q['statement']!r}"
            )


# --- Qualidade dos distratores ---


class TestDistractorQuality:
    """Garante que os distratores são plausíveis o bastante para enganar.

    Regras:
    1. Nenhum distrator pode ser uma frase preguiçosa conhecida (banlist).
    2. Cada distrator deve ter ≥ 3 palavras E ≥ 14 caracteres,
       a menos que a alternativa CORRETA também seja curta (≤ 4 palavras).
       Nesse caso aceitamos distratores na mesma escala (siglas plausíveis,
       ex.: correta "S3" vs "EC2", "RDS", "VPC").
    3. Distratores não podem ser drasticamente mais curtos que a correta;
       isso vira pista visual da resposta. Aceitamos distratores com pelo
       menos 35% do tamanho da correta OU 25 caracteres absolutos.
    """

    def _correct_is_short(self, q: dict) -> bool:
        return _word_count(q["choices"][q["correct_index"]]) <= 4

    @pytest.mark.parametrize("level", ["junior", "pleno", "senior"])
    def test_nenhum_distrator_eh_frase_preguicosa(self, level):
        questions = ALL_INTERVIEW_QUESTIONS[level]
        ofensores = []
        for i, q in enumerate(questions):
            for j, choice in enumerate(q["choices"]):
                if j == q["correct_index"]:
                    continue
                if _is_lazy(choice):
                    ofensores.append(
                        f"  {level}#{i} ({q['category']}) distrator[{j}] = {choice!r}"
                    )
        assert not ofensores, (
            "Distratores preguiçosos detectados; substitua por opções "
            "plausíveis (sintaxe vizinha, half-truth, conceito correlato):\n"
            + "\n".join(ofensores[:25])
            + (f"\n... e mais {len(ofensores) - 25}" if len(ofensores) > 25 else "")
        )

    @pytest.mark.parametrize("level", ["junior", "pleno", "senior"])
    def test_distratores_tem_substancia_minima(self, level):
        """Mínimo de palavras/caracteres, exceto quando a correta é curta."""
        questions = ALL_INTERVIEW_QUESTIONS[level]
        ofensores = []
        for i, q in enumerate(questions):
            short_correct = self._correct_is_short(q)
            for j, choice in enumerate(q["choices"]):
                if j == q["correct_index"]:
                    continue
                wc = _word_count(choice)
                cc = len(choice.strip())
                if short_correct:
                    # Para questões com correta curta, mínimo é 1 palavra/2 chars.
                    if wc < 1 or cc < 2:
                        ofensores.append(
                            f"  {level}#{i} distrator[{j}] curto demais: {choice!r}"
                        )
                else:
                    if wc < 3 or cc < 14:
                        ofensores.append(
                            f"  {level}#{i} ({q['category']}) distrator[{j}] "
                            f"sem substância ({wc} palavras, {cc} chars): {choice!r}"
                        )
        assert not ofensores, (
            "Distratores curtos demais para serem plausíveis "
            "(use frases completas com pegada técnica):\n"
            + "\n".join(ofensores[:25])
            + (f"\n... e mais {len(ofensores) - 25}" if len(ofensores) > 25 else "")
        )

    @pytest.mark.parametrize("level", ["junior", "pleno", "senior"])
    def test_distratores_nao_sao_drasticamente_mais_curtos_que_correta(
        self, level
    ):
        """Diferença grande de tamanho é pista visual da resposta."""
        questions = ALL_INTERVIEW_QUESTIONS[level]
        ofensores = []
        for i, q in enumerate(questions):
            correct = q["choices"][q["correct_index"]].strip()
            if self._correct_is_short(q):
                continue  # questões "siglas" são exceção
            correct_len = len(correct)
            limite = max(25, int(correct_len * 0.35))
            for j, choice in enumerate(q["choices"]):
                if j == q["correct_index"]:
                    continue
                if len(choice.strip()) < limite:
                    ofensores.append(
                        f"  {level}#{i} ({q['category']}): correta={correct_len}c, "
                        f"distrator[{j}]={len(choice.strip())}c → {choice!r}"
                    )
        assert not ofensores, (
            "Distratores muito mais curtos que a correta; vira pista visual:\n"
            + "\n".join(ofensores[:25])
            + (f"\n... e mais {len(ofensores) - 25}" if len(ofensores) > 25 else "")
        )


# --- Helpers expostos (sanity) ---


class TestQualityHelpers:
    """Garante que as heurísticas internas funcionam como esperamos."""

    def test_normalize_remove_pontuacao_e_caso(self):
        assert _normalize("Não há.") == "não há"
        assert _normalize("  IGUAIS!! ") == "iguais"

    def test_word_count_basico(self):
        assert _word_count("um dois três") == 3
        assert _word_count("S3") == 1
        # `\w+` ignora pontuação/símbolos como backticks e `>`,
        # então só "sobrescreve", "o" e "arquivo" são contados.
        assert _word_count("`>` sobrescreve o arquivo") == 3

    def test_is_lazy_pega_frases_classicas(self):
        assert _is_lazy("Não há motivo.") is True
        assert _is_lazy("Sem buffer.") is True
        assert _is_lazy("Apenas marketing.") is True
        assert _is_lazy("Sorteio.") is True
        assert _is_lazy("Festa de comemoração.") is True
        assert _is_lazy("Iguais.") is True
        assert _is_lazy(
            "Pull baixa apenas tags e nunca atualiza branches locais."
        ) is False
        assert _is_lazy(
            "Lista os processos com snapshot único, sem atualização periódica."
        ) is False
