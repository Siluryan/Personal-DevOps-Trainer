"""Middleware que força o teste de admissão antes do acesso às áreas internas."""
from django.shortcuts import redirect
from django.urls import resolve, reverse

ALWAYS_ALLOWED_URL_NAMES = {
    "core:landing",
    "assessments:start",
    "assessments:take",
    "assessments:result",
    "assessments:retake",
    "donations:index",
}

ALWAYS_ALLOWED_NAMESPACES = {
    "admin",
    "account",  # allauth
}


class AdmissionGateMiddleware:
    """Bloqueia rotas internas para quem ainda não passou no teste."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and not user.admission_passed and not user.is_staff:
            try:
                match = resolve(request.path_info)
            except Exception:  # noqa: BLE001
                return self.get_response(request)

            full_name = match.view_name or ""
            namespace = match.namespace or ""

            if namespace in ALWAYS_ALLOWED_NAMESPACES:
                return self.get_response(request)
            if full_name in ALWAYS_ALLOWED_URL_NAMES:
                return self.get_response(request)
            if request.path_info.startswith("/static/") or request.path_info.startswith("/media/"):
                return self.get_response(request)

            return redirect(reverse("assessments:start"))
        return self.get_response(request)
