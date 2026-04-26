"""Dados estruturados das 6 fases e 60 tópicos da trilha DevSecOps.

Cada tópico segue o schema:

    {
        "title": str,
        "summary": str,
        "lesson": {"intro": str, "body": str, "practical": str},
        "materials": [{"title", "url", "kind", "description"}, ...],
        "questions": [
            {
                "statement": str,
                "explanation": str,
                "choices": [{"text": str, "correct": bool}, ...]
            },
            ...  # 10 itens
        ],
    }
"""
from .phase1 import PHASE1
from .phase2 import PHASE2
from .phase3 import PHASE3
from .phase4 import PHASE4
from .phase5 import PHASE5
from .phase6 import PHASE6

PHASES = [PHASE1, PHASE2, PHASE3, PHASE4, PHASE5, PHASE6]

__all__ = ["PHASES"]
