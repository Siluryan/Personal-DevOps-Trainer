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


class Phase(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "fase"
        verbose_name_plural = "fases"

    def __str__(self) -> str:
        return f"Fase {self.order}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Topic(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField(blank=True)
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


class Material(models.Model):
    KIND_CHOICES = [
        ("article", "Artigo"),
        ("video", "Vídeo"),
        ("docs", "Documentação oficial"),
        ("book", "Livro/Capítulo"),
        ("course", "Curso"),
        ("tool", "Ferramenta"),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=255)
    url = models.URLField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="article")
    description = models.TextField(blank=True)
    language = models.CharField(max_length=8, default="pt-br")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["topic_id", "order", "id"]
        verbose_name = "material"
        verbose_name_plural = "materiais"

    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    """Conteúdo principal da aula, em Markdown leve / HTML simples."""

    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name="lesson")
    intro = models.TextField(blank=True, help_text="Por que este tópico importa.")
    body = models.TextField(blank=True, help_text="Aula completa (HTML/Markdown).")
    practical = models.TextField(blank=True, help_text="Exercício prático sugerido.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Aula: {self.topic.title}"


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    statement = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["topic_id", "order", "id"]

    def __str__(self) -> str:
        return self.statement[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "order", "id"]

    def __str__(self) -> str:
        return self.text
