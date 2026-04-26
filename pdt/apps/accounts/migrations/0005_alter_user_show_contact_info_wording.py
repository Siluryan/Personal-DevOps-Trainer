from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_show_on_map_default"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="show_contact_info",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Quando marcado, outros usuários podem ver seu LinkedIn, GitHub, país e bio "
                    "(no ranking, na página pública do perfil e onde o seu nome for exibido com detalhes)."
                ),
                verbose_name="deixar informações de contato visíveis para outros usuários",
            ),
        ),
    ]
