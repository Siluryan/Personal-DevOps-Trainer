from django.urls import path

from . import views

app_name = "interviews"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<str:level>/iniciar/", views.StartView.as_view(), name="start"),
    path("attempt/<int:pk>/", views.TakeView.as_view(), name="take"),
    path("attempt/<int:pk>/finalizar/", views.FinishView.as_view(), name="finish"),
    path("attempt/<int:pk>/resultado/", views.ResultView.as_view(), name="result"),
    path("attempt/<int:pk>/descartar/", views.CancelView.as_view(), name="cancel"),
]
