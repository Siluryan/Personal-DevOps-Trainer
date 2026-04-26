from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_alter_user_show_contact_info_wording"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="help_notifications_enabled",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Quando marcado, você recebe avisos de novas mensagens/atualizações da sala "
                    "de ajuda enquanto navega em outras seções da plataforma."
                ),
                verbose_name="receber notificações de ajuda",
            ),
        ),
    ]
