from django.urls import path

from . import views

app_name = "gamification"

urlpatterns = [
    path("", views.LeaderboardView.as_view(), name="leaderboard"),
    path("radar/", views.MyRadarView.as_view(), name="radar"),
]
