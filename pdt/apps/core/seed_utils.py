"""Utilitários compartilhados pelos seeds de conteúdo."""
from __future__ import annotations

import hashlib
import random


def shuffle_seeded(items: list, key: str) -> None:
    """Embaralha `items` no lugar, de forma estável e reprodutível.

    O `random.shuffle` global usa uma semente diferente a cada processo
    Python, então a ordem das alternativas mudava a cada import — ou seja, a
    cada restart do container. Isso impedia até de falar "a alternativa C" ao
    revisar uma questão, e fazia o seed reescrever a ordem sem motivo algum.

    Derivando a semente do enunciado, a mesma questão produz sempre a mesma
    ordem, em qualquer máquina, sem devolver a correta para a primeira posição.
    """
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    random.Random(int.from_bytes(digest[:8], "big")).shuffle(items)
