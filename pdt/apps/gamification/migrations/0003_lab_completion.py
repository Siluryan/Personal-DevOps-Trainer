import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gamification", "0002_choice_text_snapshot"),
        ("courses", "0003_lab"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="topicscore",
            name="lab_bonus",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="LabCompletion",
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
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "lab",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="completions",
                        to="courses.lab",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lab_completions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "conclusão de laboratório",
                "verbose_name_plural": "conclusões de laboratório",
                "ordering": ["-completed_at"],
                "unique_together": {("user", "lab")},
            },
        ),
    ]
