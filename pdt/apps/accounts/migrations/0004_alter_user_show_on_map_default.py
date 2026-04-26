from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_career_level"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="show_on_map",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Necessário para aparecer no mapa e para usar «Pedir ajuda»: sem esta opção "
                    "outros não veem seu pin e a plataforma não aceita novos pedidos de ajuda."
                ),
                verbose_name="aparecer no mapa de presença",
            ),
        ),
    ]
