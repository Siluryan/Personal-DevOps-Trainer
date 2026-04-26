from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.TrackView.as_view(), name="track"),
    path("topico/<slug:slug>/", views.TopicDetailView.as_view(), name="topic_detail"),
    path("topico/<slug:slug>/quiz/", views.QuizView.as_view(), name="quiz"),
    path("topico/<slug:slug>/quiz/resultado/<int:attempt_id>/",
         views.QuizResultView.as_view(), name="quiz_result"),
]
