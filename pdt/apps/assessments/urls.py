from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.StartView.as_view(), name="start"),
    path("teste/", views.TakeView.as_view(), name="take"),
    path("resultado/<int:pk>/", views.ResultView.as_view(), name="result"),
    path("refazer/", views.RetakeView.as_view(), name="retake"),
]
