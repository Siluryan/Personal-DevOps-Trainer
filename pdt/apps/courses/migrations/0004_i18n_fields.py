from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_lab"),
    ]

    operations = [
        migrations.AddField(
            model_name="phase",
            name="name_en",
            field=models.CharField(blank=True, default="", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="phase",
            name="description_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="topic",
            name="title_en",
            field=models.CharField(blank=True, default="", max_length=180),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="topic",
            name="summary_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="material",
            name="title_en",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="material",
            name="description_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lesson",
            name="intro_en",
            field=models.TextField(blank=True, default="", help_text="Versão em inglês de `intro`."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lesson",
            name="body_en",
            field=models.TextField(blank=True, default="", help_text="Versão em inglês de `body`."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lesson",
            name="practical_en",
            field=models.TextField(blank=True, default="", help_text="Versão em inglês de `practical`."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="question",
            name="statement_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="question",
            name="explanation_en",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="choice",
            name="text_en",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lab",
            name="title_en",
            field=models.CharField(blank=True, default="", max_length=140),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lab",
            name="spec_en",
            field=models.JSONField(
                blank=True,
                null=True,
                help_text=(
                    "Versão em inglês de `spec`: JSON completo (mesmo formato do "
                    "`kind`), não um diff — quando presente, substitui `spec` inteiro "
                    "na interface em inglês."
                ),
            ),
        ),
    ]
