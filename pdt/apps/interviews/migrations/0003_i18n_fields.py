from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interviews", "0002_interviewattempt_last_question_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="interviewquestion",
            name="statement_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="choices_en",
            field=models.JSONField(
                blank=True,
                null=True,
                help_text="Versão em inglês de `choices`: lista completa, mesma ordem, não um diff.",
            ),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="explanation_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
