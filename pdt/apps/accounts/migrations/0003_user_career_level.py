from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_show_contact_info"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="career_level",
            field=models.CharField(
                choices=[
                    ("estagiario", "Estagiário"),
                    ("junior", "Júnior"),
                    ("pleno", "Pleno"),
                    ("senior", "Sênior"),
                ],
                default="estagiario",
                help_text=(
                    "Definido pelo simulador de entrevistas. Sobe ao atingir 80%+ "
                    "no teste do próximo nível."
                ),
                max_length=12,
                verbose_name="nível de carreira",
            ),
        ),
    ]
