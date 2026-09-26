"""Equivalência de comandos montados por token no laboratório.

O gabarito guarda uma ordem. Várias ordens são o mesmo comando: flags
independentes trocam de lugar (`journalctl -p err -S today` e
`journalctl -S today -p err`) e, em algumas ferramentas, a flag pode
ficar antes ou depois do argumento (`dig +short exemplo.com`).

Em docker, git, sudo e pre-commit, atravessar um argumento muda o
comando (`docker run -d nginx --name web` não é
`docker run -d --name web nginx`). Nessas, a flag tem de permanecer
no mesmo vão entre os argumentos posicionais.
"""
from __future__ import annotations

# Flag que consome o token seguinte. `-t` entra aqui: no fim da linha,
# sem token depois, continua sendo flag solta (`sshd -t`).
VALUED_FLAGS = frozenset(
    {
        "-eo",
        "-perm",
        "-type",
        "-name",
        "-m",
        "-p",
        "-S",
        "-n",
        "-o",
        "-t",
        "-b",
        "-u",
        "-f",
        "-c",
        "--severity",
        "--exit-code",
        "--name",
        "--network",
        "--shell",
        "--home-dir",
        "--namespace",
        "--publish-url",
    }
)

# Mover a flag para outro vão muda o sentido do comando.
STICKY_BINS = frozenset({"docker", "git", "sudo", "pre-commit"})


def _is_flag(token: str) -> bool:
    return (token.startswith("-") or token.startswith("+")) and token not in {"-", "--"}


def _scan(tokens: list[str]) -> tuple[list[str], list[list[tuple[str, ...]]]]:
    """Positionals em ordem e, em cada vão entre eles, os grupos de flag."""
    pos: list[str] = []
    gaps: list[list[tuple[str, ...]]] = [[]]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if _is_flag(tok):
            if tok in VALUED_FLAGS and i + 1 < len(tokens):
                gaps[-1].append((tok, tokens[i + 1]))
                i += 2
                continue
            gaps[-1].append((tok,))
            i += 1
            continue
        pos.append(tok)
        gaps.append([])
        i += 1
    return pos, gaps


def command_key(tokens: list[str]) -> tuple:
    if not tokens:
        return ()
    binary, rest = tokens[0], tokens[1:]
    pos, gaps = _scan(rest)
    if binary in STICKY_BINS:
        frozen = tuple(tuple(sorted(gap)) for gap in gaps)
        return ("sticky", binary, tuple(pos), frozen)
    flags = tuple(sorted(flag for gap in gaps for flag in gap))
    return ("free", binary, tuple(pos), flags)


def commands_equivalent(left: list[str], right: list[str]) -> bool:
    return bool(left) and bool(right) and command_key(left) == command_key(right)
