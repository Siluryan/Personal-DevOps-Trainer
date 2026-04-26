import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.courses.models import Phase, Topic
from apps.gamification.services import build_radar_payload, top_users


class LandingView(TemplateView):
    template_name = "core/landing.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "admission_passed", False):
            return redirect("core:dashboard")
        return super().get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["phases"] = Phase.objects.prefetch_related("topics").all()
        ctx["topics_total"] = Topic.objects.count()
        ctx["radar"] = build_radar_payload(self.request.user)
        users = list(top_users(limit=10))
        ctx["leaderboard"] = users
        # Serializar dados de contato para uso no Alpine.js (apenas quem optou)
        ctx["leaderboard_contacts_json"] = json.dumps(
            {
                str(u.pk): {
                    "name": u.display_name,
                    "country": u.country,
                    "bio": u.bio,
                    "linkedin": u.linkedin_url,
                    "github": u.github_url,
                    "total": u.total,
                    "show_contact": u.show_contact_info,
                    "career": u.career_label,
                }
                for u in users
            }
        )
        return ctx
