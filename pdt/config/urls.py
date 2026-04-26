from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("apps.core.urls", namespace="core")),
    path("perfil/", include("apps.accounts.urls", namespace="accounts")),
    path("admissao/", include("apps.assessments.urls", namespace="assessments")),
    path("trilha/", include("apps.courses.urls", namespace="courses")),
    path("ranking/", include("apps.gamification.urls", namespace="gamification")),
    path("mapa/", include("apps.presence.urls", namespace="presence")),
    path("apoie/", include("apps.donations.urls", namespace="donations")),
    path("entrevistas/", include("apps.interviews.urls", namespace="interviews")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
