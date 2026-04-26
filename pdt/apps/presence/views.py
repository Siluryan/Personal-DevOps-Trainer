"""Views REST simples + página do mapa e da sala de ajuda."""
from __future__ import annotations

import secrets

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.courses.models import Topic
from apps.gamification.models import TopicScore

from .consumers import PRESENCE_GROUP
from .help_consumer import help_group_name
from .models import HelpChatMessage, HelpRequest, PresenceState
from .online_payload import build_online_users_payload


def _broadcast_refresh():
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(PRESENCE_GROUP, {"type": "presence.refresh"})


class MapView(LoginRequiredMixin, TemplateView):
    template_name = "presence/map.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["topics"] = Topic.objects.select_related("phase").order_by(
            "phase__order", "order"
        )
        ctx["open_help"] = (
            HelpRequest.objects.filter(
                requester=self.request.user,
                status__in=[HelpRequest.OPEN, HelpRequest.JOINED],
            )
            .select_related("topic")
            .first()
        )
        ctx["user_can_request_help"] = self.request.user.show_on_map
        return ctx


@login_required
def online_users(request):
    return JsonResponse({"users": build_online_users_payload()})


@login_required
@require_POST
def checkin(request):
    try:
        lat = float(request.POST["lat"])
        lng = float(request.POST["lng"])
    except (KeyError, ValueError, TypeError):
        return JsonResponse({"error": "lat/lng obrigatórios"}, status=400)

    state, _ = PresenceState.objects.get_or_create(user=request.user)
    state.latitude = lat
    state.longitude = lng
    has_open_help = HelpRequest.objects.filter(
        requester=request.user,
        status__in=[HelpRequest.OPEN, HelpRequest.JOINED],
    ).exists()
    if has_open_help:
        state.status = PresenceState.HELP
    elif state.status == PresenceState.OFFLINE:
        state.status = PresenceState.AVAILABLE
    state.save()
    _broadcast_refresh()
    return JsonResponse({"ok": True, "status": state.status})


@login_required
@require_POST
def create_help_request(request):
    if not request.user.show_on_map:
        return JsonResponse(
            {
                "error": (
                    "Para pedir ajuda pela plataforma, ative «Aparecer no mapa de presença» "
                    "no seu perfil. Sem isso, seu pedido não é aceito."
                )
            },
            status=403,
        )
    topic_id = request.POST.get("topic_id")
    description = (request.POST.get("description") or "").strip()
    topic = get_object_or_404(Topic, pk=topic_id)

    open_qs = HelpRequest.objects.filter(
        requester=request.user, status__in=[HelpRequest.OPEN, HelpRequest.JOINED]
    )
    HelpChatMessage.objects.filter(help_request__in=open_qs).delete()
    open_qs.update(status=HelpRequest.CANCELLED)

    help_request = HelpRequest.objects.create(
        requester=request.user,
        topic=topic,
        description=description,
        room_token=secrets.token_urlsafe(16),
    )
    state, _ = PresenceState.objects.get_or_create(user=request.user)
    state.status = PresenceState.HELP
    state.save(update_fields=["status", "last_seen"])
    _broadcast_refresh()
    return JsonResponse(
        {
            "ok": True,
            "id": help_request.id,
            "room_token": help_request.room_token,
            "topic": topic.title,
            "help_url": reverse("presence:help_room", args=[help_request.id]),
        }
    )


@login_required
@require_POST
def join_help_request(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk)
    if help_request.requester_id == request.user.id:
        return JsonResponse({"error": "Você é quem pediu a ajuda."}, status=400)
    if help_request.status != HelpRequest.OPEN:
        return JsonResponse({"error": "Solicitação não está aberta."}, status=400)

    help_request.helper = request.user
    help_request.status = HelpRequest.JOINED
    help_request.save(update_fields=["helper", "status"])
    _broadcast_refresh()
    return JsonResponse({"ok": True, "redirect": f"/mapa/ajuda/{help_request.id}/"})


@login_required
@require_POST
def resolve_help_request(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk, requester=request.user)
    if help_request.status not in [HelpRequest.OPEN, HelpRequest.JOINED]:
        return JsonResponse({"error": "Solicitação já encerrada."}, status=400)

    help_request.status = HelpRequest.RESOLVED
    help_request.resolved_at = timezone.now()
    help_request.save(update_fields=["status", "resolved_at"])
    HelpChatMessage.objects.filter(help_request=help_request).delete()
    layer = get_channel_layer()
    if layer:
        async_to_sync(layer.group_send)(
            help_group_name(help_request.id),
            {
                "type": "help.system",
                "kind": "resolved",
                "user_id": request.user.id,
                "name": request.user.display_name,
                "ts": timezone.now().isoformat(),
            },
        )

    if help_request.helper:
        TopicScore.add_help_bonus(
            user=help_request.helper, topic=help_request.topic, amount=1
        )

    state, _ = PresenceState.objects.get_or_create(user=request.user)
    state.status = PresenceState.AVAILABLE
    state.save(update_fields=["status", "last_seen"])
    _broadcast_refresh()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def cancel_help_request(request, pk):
    help_request = get_object_or_404(HelpRequest, pk=pk, requester=request.user)
    if help_request.status not in [HelpRequest.OPEN, HelpRequest.JOINED]:
        return JsonResponse({"error": "Solicitação já encerrada."}, status=400)
    help_request.status = HelpRequest.CANCELLED
    help_request.save(update_fields=["status"])
    HelpChatMessage.objects.filter(help_request=help_request).delete()
    state, _ = PresenceState.objects.get_or_create(user=request.user)
    state.status = PresenceState.AVAILABLE
    state.save(update_fields=["status", "last_seen"])
    _broadcast_refresh()
    return JsonResponse({"ok": True})


class HelpRoomView(LoginRequiredMixin, TemplateView):
    """Sala de ajuda, chat de texto + voz nativos via WebRTC.

    A negociação WebRTC (offer/answer/ICE) é feita pelo `HelpRoomConsumer`
    usando o WebSocket `/ws/help/<id>/`. O frontend abre a câmera/mic do
    usuário (apenas mic neste momento) e troca SDP com o peer.
    """

    template_name = "presence/help_room.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        help_request = get_object_or_404(HelpRequest, pk=kwargs["pk"])
        if (
            help_request.requester_id != self.request.user.id
            and help_request.helper_id != self.request.user.id
        ):
            ctx["forbidden"] = True
        else:
            ctx["forbidden"] = False
        ctx["help_request"] = help_request
        ctx["ice_servers"] = settings.WEBRTC_ICE_SERVERS
        if not ctx["forbidden"]:
            qs = (
                HelpChatMessage.objects.filter(help_request=help_request)
                .select_related("author")
                .order_by("created_at")[:500]
            )
            ctx["help_chat_history"] = [
                {
                    "name": m.author.display_name,
                    "text": m.body,
                    "self": m.author_id == self.request.user.id,
                }
                for m in qs
            ]
        else:
            ctx["help_chat_history"] = []
        return ctx
