from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("setup/", views.ProfileSetupView.as_view(), name="profile_setup"),
    path("editar/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("u/<int:pk>/", views.ProfileDetailView.as_view(), name="profile"),
]
