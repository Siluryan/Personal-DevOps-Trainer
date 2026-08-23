from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="glossaryterm",
            name="term_en",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Grafia do termo como aparece no texto em inglês da aula, se for "
                    "diferente do português (siglas como RCE/IAM geralmente não mudam "
                    "e podem ficar em branco aqui)."
                ),
                max_length=64,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="glossaryterm",
            name="definition_en",
            field=models.CharField(blank=True, default="", max_length=300),
            preserve_default=False,
        ),
    ]
