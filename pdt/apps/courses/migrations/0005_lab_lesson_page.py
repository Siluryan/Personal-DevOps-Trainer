from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_i18n_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="lab",
            name="lesson_page",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text=(
                    "Página da aula (1 = primeira) em que este lab aparece. "
                    "A paginação é a mesma de `paginate_lesson_body`."
                ),
            ),
        ),
        migrations.AlterModelOptions(
            name="lab",
            options={
                "ordering": ["topic_id", "lesson_page", "order", "id"],
                "verbose_name": "laboratório",
                "verbose_name_plural": "laboratórios",
            },
        ),
        migrations.AlterUniqueTogether(
            name="lab",
            unique_together={("topic", "lesson_page")},
        ),
    ]
