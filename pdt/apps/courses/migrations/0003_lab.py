import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_seed_managed"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lab",
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
                    "kind",
                    models.CharField(
                        choices=[
                            ("terminal", "Terminal — montar comando tocando nos tokens"),
                            ("find_flaw", "Caça-a-falha — tocar na linha vulnerável"),
                            ("order", "Ordenação — pôr as etapas na ordem certa"),
                            ("blanks", "Lacunas — completar config escolhendo o valor"),
                            ("scenario", "Cenário — decidir e ver a consequência"),
                        ],
                        max_length=16,
                    ),
                ),
                ("title", models.CharField(max_length=140)),
                (
                    "spec",
                    models.JSONField(
                        help_text=(
                            "Conteúdo do lab; o formato depende de `kind` "
                            "(ver seed_data/labs.py)."
                        )
                    ),
                ),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "seed_managed",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Enquanto marcado, `seed_labs` mantém este lab sincronizado com "
                            "apps/courses/seed_data/labs.py. Salvar pelo admin desmarca "
                            "automaticamente — a partir daí o seed não sobrescreve a edição."
                        ),
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="labs",
                        to="courses.topic",
                    ),
                ),
            ],
            options={
                "verbose_name": "laboratório",
                "verbose_name_plural": "laboratórios",
                "ordering": ["topic_id", "order", "id"],
            },
        ),
    ]
