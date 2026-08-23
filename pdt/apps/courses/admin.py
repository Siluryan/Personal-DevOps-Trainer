from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import TextField
from django.forms.models import BaseInlineFormSet

from .models import Choice, Lesson, Material, Phase, Question, Topic


class SeedLockingAdminMixin:
    """Marca `seed_managed=False` ao editar qualquer campo pelo admin.

    A partir daí, `seed_topics` para de sobrescrever este registro — é o que
    torna editar uma aula ou questão pelo admin uma mudança que sobrevive ao
    próximo restart do container, em vez de ser revertida no dia seguinte.

    Se o próprio `seed_managed` foi mexido no formulário, respeita a escolha
    explícita do mantenedor (ex.: religar o campo para voltar a sincronizar
    com o seed) em vez de forçá-lo de volta a False — senão o checkbox
    apareceria no form mas nunca "colaria" o valor marcado.
    """

    def save_model(self, request, obj, form, change):
        if "seed_managed" not in form.changed_data and form.changed_data:
            obj.seed_managed = False
        super().save_model(request, obj, form, change)


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


class ChoiceInlineFormSet(BaseInlineFormSet):
    """Impede salvar uma questão sem exatamente uma alternativa correta.

    Antes disso, o inline padrão aceitava salvar com zero corretas (o quiz
    nunca pontuaria) ou com duas (a segunda seria ignorada em silêncio na
    correção) — sem nenhum aviso na hora de salvar.
    """

    def clean(self):
        super().clean()
        total = 0
        corretas = 0
        for form in self.forms:
            data = getattr(form, "cleaned_data", None)
            if not data or data.get("DELETE"):
                continue
            total += 1
            if data.get("is_correct"):
                corretas += 1
        if total and corretas != 1:
            raise ValidationError(
                f"Esta questão tem {corretas} alternativa(s) marcada(s) como correta — "
                "precisa ser exatamente 1."
            )


class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormSet
    extra = 0
    min_num = 2
    validate_min = True


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "phase", "order")
    list_filter = ("phase",)
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [MaterialInline]


@admin.register(Lesson)
class LessonAdmin(SeedLockingAdminMixin, admin.ModelAdmin):
    list_display = ("topic", "seed_managed", "updated_at")
    list_filter = ("seed_managed",)
    search_fields = ("topic__title",)
    readonly_fields = ("updated_at",)
    fields = ("topic", "seed_managed", "intro", "body", "practical", "updated_at")
    # Textarea padrão é 10 linhas — inviável para uma aula com mediana de
    # 7.700 caracteres de HTML. Fonte monoespaçada ajuda a ver as tags.
    formfield_overrides = {
        TextField: {
            "widget": forms.Textarea(
                attrs={"rows": 24, "style": "font-family: ui-monospace, monospace; width: 100%"}
            )
        },
    }


@admin.register(Question)
class QuestionAdmin(SeedLockingAdminMixin, admin.ModelAdmin):
    list_display = ("topic", "statement", "is_active", "seed_managed")
    list_filter = ("topic__phase", "is_active", "seed_managed")
    search_fields = ("statement",)
    inlines = [ChoiceInline]
