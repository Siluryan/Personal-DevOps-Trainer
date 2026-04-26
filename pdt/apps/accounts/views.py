from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from apps.gamification.services import build_radar_payload, total_score_for

from .forms import ProfileEditForm, ProfileSetupForm
from .models import User


class ProfileSetupView(LoginRequiredMixin, UpdateView):
    """Pós-cadastro: coleta dados de carreira (LinkedIn/GitHub)."""

    form_class = ProfileSetupForm
    template_name = "accounts/profile_setup.html"
    success_url = reverse_lazy("assessments:start")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Perfil salvo. Agora faça o teste de admissão para liberar a plataforma.",
        )
        return super().form_valid(form)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("core:dashboard")

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDetailView(DetailView):
    model = User
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["radar"] = build_radar_payload(self.object)
        ctx["total_score"] = total_score_for(self.object)
        return ctx
