import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.courses.models import Phase, Topic
from apps.gamification.services import build_radar_payload, top_users, total_score_for


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
        ctx["my_total_score"] = total_score_for(self.request.user)
        users = list(top_users(limit=10))
        ctx["leaderboard"] = users
        # Dados de contato para o painel em Alpine.js.
        #
        # Os campos de contato só entram no payload de quem marcou
        # `show_contact_info`. Antes iam para todo mundo e a ocultação
        # acontecia só no template (`x-if="selected.show_contact"`), ou seja,
        # bio, país, LinkedIn e GitHub de quem NÃO optou ficavam legíveis no
        # HTML da página para qualquer um que abrisse o "ver código-fonte".
        ctx["leaderboard_contacts_json"] = json.dumps(
            {
                str(u.pk): {
                    "name": u.display_name,
                    "total": int(u.total or 0),
                    "show_contact": bool(u.show_contact_info),
                    "career": u.career_label,
                    "profile_url": reverse("accounts:profile", args=[u.pk]),
                    **(
                        {
                            "country": u.country,
                            "bio": u.bio,
                            "linkedin": u.linkedin_url,
                            "github": u.github_url,
                        }
                        if u.show_contact_info
                        else {}
                    ),
                }
                for u in users
            }
        )
        return ctx
