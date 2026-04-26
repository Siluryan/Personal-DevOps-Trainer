#!/usr/bin/env python
"""Utilitário de linha de comando do Django para o PDT."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Confirme que o pacote está instalado e o "
            "ambiente virtual está ativo."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
