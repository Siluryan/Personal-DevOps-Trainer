from django.contrib import admin

from .models import Choice, Lesson, Material, Phase, Question, Topic


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0
    fields = ("order", "title", "slug")
    readonly_fields = ("slug",)


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ("order", "name")
    ordering = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TopicInline]


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "phase", "order")
    list_filter = ("phase",)
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [MaterialInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("topic", "updated_at")
    search_fields = ("topic__title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("topic", "statement", "is_active")
    list_filter = ("topic__phase", "is_active")
    search_fields = ("statement",)
    inlines = [ChoiceInline]
