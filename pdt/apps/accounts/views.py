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
    """Perfil de um usuário.

    Antes era aberto na internet, com PK sequencial na URL — dava para varrer
    1, 2, 3… e listar toda a base, cada um com nome, nível e radar de estudo.

    Agora o acesso anônimo só alcança quem optou por aparecer publicamente
    (`show_in_leaderboard`). Para os demais, o filtro de queryset devolve 404,
    igual ao de um PK inexistente — então o visitante anônimo não consegue nem
    distinguir "não existe" de "existe e é privado", que é o que fecha a
    enumeração. Quem está logado continua vendo qualquer perfil.

    A flag escolhida é `show_in_leaderboard` porque é a única que já significa
    "aceito aparecer numa página pública": o ranking é anônimo e linka para
    estes perfis, então usá-la mantém aqueles links funcionando.
    """

    model = User
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile_user"

    def get_queryset(self):
        qs = User.objects.all()
        if not self.request.user.is_authenticated:
            qs = qs.filter(show_in_leaderboard=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["radar"] = build_radar_payload(self.object)
        ctx["total_score"] = total_score_for(self.object)
        return ctx
