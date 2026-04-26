from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import build_radar_payload, top_users, total_score_for


class LeaderboardView(TemplateView):
    template_name = "gamification/leaderboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users"] = top_users(50)
        return ctx


class MyRadarView(LoginRequiredMixin, TemplateView):
    template_name = "gamification/radar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["radar"] = build_radar_payload(self.request.user)
        ctx["total_score"] = total_score_for(self.request.user)
        return ctx
