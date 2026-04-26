from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import build_radar_payload, top_users, total_score_for


class LeaderboardView(TemplateView):
    template_name = "gamification/leaderboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users"] = top_users(50)
        return ctx

    def render_to_response(self, context, **response_kwargs):
        # Evita resposta cacheada por browser/proxy/CDN em produção.
        response = super().render_to_response(context, **response_kwargs)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


class MyRadarView(LoginRequiredMixin, TemplateView):
    template_name = "gamification/radar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["radar"] = build_radar_payload(self.request.user)
        ctx["total_score"] = total_score_for(self.request.user)
        return ctx
