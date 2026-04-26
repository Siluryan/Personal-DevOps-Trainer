from django.contrib import admin

from .models import TopicAttempt, TopicAttemptAnswer, TopicScore


@admin.register(TopicAttempt)
class TopicAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "score", "total_questions", "finished_at")
    list_filter = ("topic__phase",)
    search_fields = ("user__email", "topic__title")


@admin.register(TopicAttemptAnswer)
class TopicAttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct")


@admin.register(TopicScore)
class TopicScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "points", "best_quiz_score", "help_bonus", "updated_at")
    list_filter = ("topic__phase",)
    search_fields = ("user__email", "topic__title")
