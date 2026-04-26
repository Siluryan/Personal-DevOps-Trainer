from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="interviewattempt",
            name="last_question_index",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Última questão exibida (0-based); usada para retomar ao clicar Continuar.",
            ),
        ),
    ]
