"""Modelos de presença e pedidos de ajuda no mapa."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class PresenceState(models.Model):
    """Localização aproximada e status do usuário no mapa."""

    AVAILABLE = "available"
    HELP = "help"
    OFFLINE = "offline"
    STATUS_CHOICES = [
        (AVAILABLE, "Disponível"),
        (HELP, "Pedindo ajuda"),
        (OFFLINE, "Offline"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="presence",
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=OFFLINE)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user} [{self.status}]"


class HelpRequest(models.Model):
    """Pedido de ajuda associado a um tópico (escolhido pelo usuário)."""

    OPEN = "open"
    JOINED = "joined"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (OPEN, "Aberto"),
        (JOINED, "Em atendimento"),
        (RESOLVED, "Resolvido"),
        (CANCELLED, "Cancelado"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="help_requests",
    )
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="helped_requests",
    )
    topic = models.ForeignKey(
        "courses.Topic",
        on_delete=models.PROTECT,
        related_name="help_requests",
        help_text="Tópico em que o usuário está com dificuldade.",
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=OPEN)
    room_token = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Ajuda de {self.requester} em {self.topic} [{self.status}]"


class HelpChatMessage(models.Model):
    """Mensagem de texto na sala de ajuda (persistida para histórico após refresh)."""

    help_request = models.ForeignKey(
        HelpRequest,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="help_chat_messages",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["help_request", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Chat #{self.pk} em ajuda {self.help_request_id}"
