from django.contrib import admin

from .models import AdmissionAttempt, AdmissionChoice, AdmissionQuestion


class ChoiceInline(admin.TabularInline):
    model = AdmissionChoice
    extra = 4


@admin.register(AdmissionQuestion)
class AdmissionQuestionAdmin(admin.ModelAdmin):
    list_display = ("statement", "area", "is_active")
    list_filter = ("area", "is_active")
    search_fields = ("statement",)
    inlines = [ChoiceInline]


@admin.register(AdmissionAttempt)
class AdmissionAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "passed", "finished_at")
    list_filter = ("passed",)
    search_fields = ("user__email",)
    readonly_fields = ("question_ids", "answers", "started_at", "finished_at")
