"""Modelagem da trilha DevSecOps.

A trilha tem 6 fases (`Phase`) e 60 tópicos (`Topic`), cada tópico é um
ponto do gráfico de desempenho do usuário. Cada tópico tem `Material`s de
referência, um `Lesson` (a aula propriamente dita) e um quiz com 10
`Question`s. As respostas viram `Attempt` + `AttemptAnswer` em outro app.
"""
from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from django.utils.translation import gettext_lazy as _

from apps.core.i18n import localized


class Phase(models.Model):
    name = models.CharField(max_length=120, unique=True)
    name_en = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "fase"
        verbose_name_plural = "fases"

    def __str__(self) -> str:
        return f"Fase {self.order}: {self.name}"

    @property
    def display_name(self) -> str:
        return localized(self.name, self.name_en)

    @property
    def display_description(self) -> str:
        return localized(self.description, self.description_en)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Topic(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=180)
    title_en = models.CharField(max_length=180, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField(blank=True)
    summary_en = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["phase__order", "order"]
        unique_together = [("phase", "order")]
        verbose_name = "tópico"
        verbose_name_plural = "tópicos"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("courses:topic_detail", args=[self.slug])

    @property
    def display_title(self) -> str:
        return localized(self.title, self.title_en)

    @property
    def display_summary(self) -> str:
        return localized(self.summary, self.summary_en)


class Material(models.Model):
    KIND_CHOICES = [
        ("article", _("Artigo")),
        ("video", _("Vídeo")),
        ("docs", _("Documentação oficial")),
        ("book", _("Livro/Capítulo")),
        ("course", _("Curso")),
        ("tool", _("Ferramenta")),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)
    url = models.URLField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="article")
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    language = models.CharField(max_length=8, default="pt-br")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["topic_id", "order", "id"]
        verbose_name = "material"
        verbose_name_plural = "materiais"

    def __str__(self) -> str:
        return self.title

    @property
    def display_title(self) -> str:
        return localized(self.title, self.title_en)

    @property
    def display_description(self) -> str:
        return localized(self.description, self.description_en)


class Lesson(models.Model):
    """Conteúdo principal da aula, em Markdown leve / HTML simples."""

    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name="lesson")
    intro = models.TextField(blank=True, help_text="Por que este tópico importa.")
    intro_en = models.TextField(blank=True, help_text="Versão em inglês de `intro`.")
    body = models.TextField(blank=True, help_text="Aula completa (HTML/Markdown).")
    body_en = models.TextField(blank=True, help_text="Versão em inglês de `body`.")
    practical = models.TextField(blank=True, help_text="Exercício prático sugerido.")
    practical_en = models.TextField(blank=True, help_text="Versão em inglês de `practical`.")
    updated_at = models.DateTimeField(auto_now=True)

    seed_managed = models.BooleanField(
        default=True,
        help_text=(
            "Enquanto marcado, `seed_topics` mantém esta aula sincronizada com "
            "apps/courses/seed_data/. Salvar pelo admin desmarca automaticamente "
            "— a partir daí o seed não sobrescreve mais o conteúdo editado."
        ),
    )

    def __str__(self) -> str:
        return f"Aula: {self.topic.title}"

    @property
    def display_intro(self) -> str:
        return localized(self.intro, self.intro_en)

    @property
    def display_body(self) -> str:
        return localized(self.body, self.body_en)

    @property
    def display_practical(self) -> str:
        return localized(self.practical, self.practical_en)


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    statement = models.TextField()
    statement_en = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    explanation_en = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    seed_managed = models.BooleanField(
        default=True,
        help_text=(
            "Enquanto marcado, `seed_topics` mantém esta questão (e suas "
            "alternativas) sincronizada com apps/courses/seed_data/. Salvar "
            "pelo admin desmarca automaticamente — a partir daí o seed não "
            "sobrescreve nem apaga mais as alternativas editadas."
        ),
    )

    class Meta:
        ordering = ["topic_id", "order", "id"]

    def __str__(self) -> str:
        return self.statement[:80]

    @property
    def display_statement(self) -> str:
        return localized(self.statement, self.statement_en)

    @property
    def display_explanation(self) -> str:
        return localized(self.explanation, self.explanation_en)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    text_en = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "order", "id"]

    def __str__(self) -> str:
        return self.text

    @property
    def display_text(self) -> str:
        return localized(self.text, self.text_en)


class Lab(models.Model):
    """Laboratório prático interativo de um tópico.

    Roda inteiramente no cliente (Alpine.js): NÃO executa comando de verdade,
    valida o raciocínio. Isso é deliberado, não limitação temporária — a
    plataforma roda numa t4g.nano (512 MB) e sandbox por aluno exigiria uma
    fleet própria; e o objetivo é o aluno conseguir estudar pelo celular,
    onde digitar `find . -type f -name '*.sh'` é inviável. Por isso todo
    formato abaixo é resolvido por TOQUE, não por digitação.

    Cada `kind` interpreta `spec` de um jeito (o schema de cada um está
    documentado em apps/courses/seed_data/labs.py). Cada página da aula
    tem o seu (`lesson_page`).
    """

    class Kind(models.TextChoices):
        TERMINAL = "terminal", _("Terminal — montar comando tocando nos tokens")
        FIND_FLAW = "find_flaw", _("Caça-a-falha — tocar na linha vulnerável")
        ORDER = "order", _("Ordenação — pôr as etapas na ordem certa")
        BLANKS = "blanks", _("Lacunas — completar config escolhendo o valor")
        SCENARIO = "scenario", _("Cenário — decidir e ver a consequência")

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="labs")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    title = models.CharField(max_length=140)
    title_en = models.CharField(max_length=140, blank=True)
    lesson_page = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Página da aula (1 = primeira) em que este lab aparece. "
            "A paginação é a mesma de `paginate_lesson_body`."
        ),
    )
    spec = models.JSONField(
        help_text="Conteúdo do lab; o formato depende de `kind` (ver seed_data/labs.py)."
    )
    spec_en = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "Versão em inglês de `spec`: JSON completo (mesmo formato do "
            "`kind`), não um diff — quando presente, substitui `spec` inteiro "
            "na interface em inglês."
        ),
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    seed_managed = models.BooleanField(
        default=True,
        help_text=(
            "Enquanto marcado, `seed_labs` mantém este lab sincronizado com "
            "apps/courses/seed_data/labs.py. Salvar pelo admin desmarca "
            "automaticamente — a partir daí o seed não sobrescreve a edição."
        ),
    )

    class Meta:
        ordering = ["topic_id", "lesson_page", "order", "id"]
        unique_together = [("topic", "lesson_page")]
        verbose_name = "laboratório"
        verbose_name_plural = "laboratórios"

    def __str__(self) -> str:
        return f"{self.topic.title} · {self.title}"

    @property
    def display_title(self) -> str:
        return localized(self.title, self.title_en)

    @property
    def display_spec(self):
        return localized(self.spec, self.spec_en)
