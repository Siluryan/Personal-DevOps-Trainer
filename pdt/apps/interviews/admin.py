from django.contrib import admin

from .models import InterviewAttempt, InterviewQuestion


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "level", "category", "statement_short", "is_active")
    list_filter = ("level", "category", "is_active")
    search_fields = ("statement", "category")

    def statement_short(self, obj):
        return obj.statement[:80]


@admin.register(InterviewAttempt)
class InterviewAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "score", "passed", "started_at", "finished_at")
    list_filter = ("level", "passed")
    search_fields = ("user__email", "user__full_name")
