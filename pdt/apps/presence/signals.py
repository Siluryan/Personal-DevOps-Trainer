"""Sinais: presença no mapa ao encerrar sessão."""
from __future__ import annotations

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .services import user_presence_mark_offline


@receiver(user_logged_out)
def clear_map_presence_on_logout(sender, request, user, **kwargs):
    """Logout destrói a sessão; o sendBeacon do cliente pode perder a corrida."""
    if user is not None:
        user_presence_mark_offline(user)
