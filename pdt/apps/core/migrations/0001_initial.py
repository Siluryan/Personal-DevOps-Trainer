from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GlossaryTerm",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "term",
                    models.CharField(
                        help_text=(
                            "Termo exato como aparece no texto das aulas (ex.: RCE, IAM, "
                            "mTLS). Sensível a maiúsculas/minúsculas."
                        ),
                        max_length=64,
                        unique=True,
                    ),
                ),
                (
                    "definition",
                    models.CharField(
                        help_text=(
                            "Explicação breve (1-2 frases) mostrada na caixinha ao clicar "
                            "no termo."
                        ),
                        max_length=300,
                    ),
                ),
                (
                    "seed_managed",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Gerenciado pelo seed automático. Editar pelo admin desliga "
                            "isso e protege sua edição."
                        ),
                    ),
                ),
            ],
            options={
                "ordering": ["term"],
            },
        ),
    ]
