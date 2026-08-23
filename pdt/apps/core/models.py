from django.db import models


class GlossaryTerm(models.Model):
    """Termo técnico ou sigla explicado numa caixinha clicável dentro do texto das aulas.

    `render_lesson` (apps.core.templatetags.pdt_extras) varre o HTML de cada
    aula e marca a primeira ocorrência de cada termo conhecido com um botão
    que, ao ser clicado, mostra `definition`.
    """

    term = models.CharField(
        max_length=64,
        unique=True,
        help_text=(
            "Termo exato como aparece no texto das aulas (ex.: RCE, IAM, mTLS). "
            "Sensível a maiúsculas/minúsculas."
        ),
    )
    definition = models.CharField(
        max_length=300,
        help_text="Explicação breve (1-2 frases) mostrada na caixinha ao clicar no termo.",
    )
    seed_managed = models.BooleanField(
        default=True,
        help_text="Gerenciado pelo seed automático. Editar pelo admin desliga isso e protege sua edição.",
    )

    class Meta:
        ordering = ["term"]

    def __str__(self) -> str:
        return self.term
