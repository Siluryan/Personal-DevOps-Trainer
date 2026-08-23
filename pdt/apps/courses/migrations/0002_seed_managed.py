from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="seed_managed",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Enquanto marcado, `seed_topics` mantém esta aula sincronizada com "
                    "apps/courses/seed_data/. Salvar pelo admin desmarca automaticamente "
                    "— a partir daí o seed não sobrescreve mais o conteúdo editado."
                ),
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="seed_managed",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Enquanto marcado, `seed_topics` mantém esta questão (e suas "
                    "alternativas) sincronizada com apps/courses/seed_data/. Salvar "
                    "pelo admin desmarca automaticamente — a partir daí o seed não "
                    "sobrescreve nem apaga mais as alternativas editadas."
                ),
            ),
        ),
    ]
