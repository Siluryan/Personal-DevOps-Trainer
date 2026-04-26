from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="show_contact_info",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Quando marcado, quem clicar no seu nome no ranking verá "
                    "seu LinkedIn, GitHub, país e bio."
                ),
                verbose_name="exibir informações de contato no ranking",
            ),
        ),
    ]
